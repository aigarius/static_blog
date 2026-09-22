#!/usr/bin/env python3
"""
Home Assistant Climate Data Exporter
Extracts climate sensor data (3 temperature, 3 humidity) from Home Assistant,
formats it into compact static JSON time-series files (including long-term monthly
archives with intelligent local caching), and pushes them to the blog server via rsync over SSH.
"""

import argparse
import asyncio
import datetime
import json
import logging
import math
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests
import websockets
import yaml

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("climate_exporter")

LATVIAN_MONTH_NAMES = {
    1: "Janvāris",
    2: "Februāris",
    3: "Marts",
    4: "Aprīlis",
    5: "Maijs",
    6: "Jūnijs",
    7: "Jūlijs",
    8: "Augusts",
    9: "Septembris",
    10: "Oktobris",
    11: "Novembris",
    12: "Decembris",
}


def load_config(config_path: Path) -> Dict[str, Any]:
    """Loads configuration from YAML file and merges environment variables."""
    if not config_path.exists():
        logger.error(f"Configuration file not found: {config_path}")
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if "HASS_URL" in os.environ:
        config["home_assistant"]["url"] = os.environ["HASS_URL"]
    if "HASS_TOKEN" in os.environ:
        config["home_assistant"]["token"] = os.environ["HASS_TOKEN"]

    return config


class HomeAssistantClient:
    """Client for interacting with Home Assistant REST and WebSocket APIs."""

    def __init__(self, base_url: str, token: str, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        self.timeout = timeout

    def get_state(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Fetch current state of an entity."""
        url = f"{self.base_url}/api/states/{entity_id}"
        try:
            resp = requests.get(url, headers=self.headers, timeout=self.timeout)
            if resp.status_code == 200:
                return resp.json()
            logger.warning(f"Error fetching state for {entity_id}: HTTP {resp.status_code} - {resp.text}")
        except Exception as e:
            logger.error(f"Failed to connect to Home Assistant at {url}: {e}")
        return None

    def get_history(
        self,
        entity_ids: List[str],
        start_time: datetime.datetime,
        end_time: Optional[datetime.datetime] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Fetch historical states for a list of entities via REST API."""
        start_iso = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        url = f"{self.base_url}/api/history/period/{start_iso}"
        params = {
            "filter_entity_id": ",".join(entity_ids),
            "significant_changes_only": "0",
            "minimal_response": "0",
            "no_attributes": "1",
        }
        if end_time:
            params["end_time"] = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")

        try:
            resp = requests.get(
                url, headers=self.headers, params=params, timeout=self.timeout
            )
            if resp.status_code == 200:
                data = resp.json()
                result: Dict[str, List[Dict[str, Any]]] = {}
                for entity_history in data:
                    if entity_history and len(entity_history) > 0:
                        eid = entity_history[0].get("entity_id")
                        if eid:
                            result[eid] = entity_history
                return result
            logger.warning(f"Error fetching history: HTTP {resp.status_code} - {resp.text}")
        except Exception as e:
            logger.error(f"Failed to fetch history from {url}: {e}")
        return {}

    def get_statistics(
        self,
        entity_ids: List[str],
        start_time: datetime.datetime,
        end_time: Optional[datetime.datetime] = None,
        period: str = "hour",
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Fetch long-term statistics via Home Assistant WebSocket API."""
        ws_url = self.base_url.replace("http://", "ws://").replace("https://", "wss://") + "/api/websocket"
        return asyncio.run(self._async_get_statistics(ws_url, entity_ids, start_time, end_time, period))

    async def _async_get_statistics(
        self,
        ws_url: str,
        entity_ids: List[str],
        start_time: datetime.datetime,
        end_time: Optional[datetime.datetime],
        period: str,
    ) -> Dict[str, List[Dict[str, Any]]]:
        start_iso = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        req = {
            "id": 1,
            "type": "recorder/statistics_during_period",
            "start_time": start_iso,
            "statistic_ids": entity_ids,
            "period": period,
        }
        if end_time:
            req["end_time"] = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")

        try:
            async with websockets.connect(ws_url, max_size=30 * 1024 * 1024, open_timeout=self.timeout) as ws:
                msg = json.loads(await ws.recv())
                if msg.get("type") != "auth_required":
                    logger.warning(f"Unexpected initial WS message: {msg}")
                await ws.send(json.dumps({"type": "auth", "access_token": self.token}))
                auth_resp = json.loads(await ws.recv())
                if auth_resp.get("type") != "auth_ok":
                    logger.error(f"WebSocket authentication failed: {auth_resp}")
                    return {}
                await ws.send(json.dumps(req))
                res = json.loads(await ws.recv())
                if res.get("success", False) or "result" in res:
                    return res.get("result", {})
                logger.warning(f"Error fetching statistics: {res}")
        except Exception as e:
            logger.error(f"WebSocket statistics query error: {e}")
        return {}


def parse_float_state(state_val: Any) -> Optional[float]:
    """Parse numeric sensor reading or return None if unavailable."""
    if state_val in (None, "unavailable", "unknown", ""):
        return None
    try:
        val = float(state_val)
        if math.isnan(val) or math.isinf(val):
            return None
        return round(val, 2)
    except (ValueError, TypeError):
        return None


def calculate_trend(current: Optional[float], past: Optional[float], threshold: float = 0.2) -> str:
    """Determine reading trend over a window."""
    if current is None or past is None:
        return "stable"
    diff = current - past
    if diff >= threshold:
        return "rising"
    elif diff <= -threshold:
        return "falling"
    return "stable"


def calculate_humidity_comfort(humidity: Optional[float]) -> str:
    """Classify humidity level."""
    if humidity is None:
        return "unknown"
    if humidity < 40.0:
        return "dry"
    elif humidity <= 60.0:
        return "ideal"
    return "humid"


def fetch_and_process_lts_history(
    client: HomeAssistantClient,
    locations: List[Dict[str, Any]],
    output_dir: Path,
    start_date_str: str = "2026-07-15",
) -> Tuple[Dict[str, Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Manages long-term monthly archives with intelligent local caching.
    Past completed months already present on disk are never re-queried from Home Assistant.
    For the current month, only new hourly points since the latest cached sample are fetched.
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    now_m_key = now.strftime("%Y-%m")
    history_dir = output_dir / "history"
    history_dir.mkdir(parents=True, exist_ok=True)

    try:
        start_date = datetime.datetime.fromisoformat(start_date_str).replace(tzinfo=datetime.timezone.utc)
    except Exception:
        start_date = datetime.datetime(2026, 7, 15, 0, 0, tzinfo=datetime.timezone.utc)

    # 1. Load existing cached monthly archives from disk
    cached_monthly: Dict[str, Dict[str, Any]] = {}
    for f in sorted(history_dir.glob("history-*.json")):
        try:
            with open(f, "r", encoding="utf-8") as fp:
                data = json.load(fp)
                m_key = data.get("period") or f.stem.replace("history-", "")
                if data.get("series") and len(data["series"]) > 0:
                    cached_monthly[m_key] = data
        except Exception as e:
            logger.warning(f"Could not read cached archive {f}: {e}")

    # Build entity list and field names
    entity_ids = []
    loc_entities = []
    for loc in locations:
        t_eid = loc["temperature"]["entity_id"]
        h_eid = loc["humidity"]["entity_id"]
        entity_ids.extend([t_eid, h_eid])
        loc_entities.append((loc["id"], t_eid, h_eid))

    fields = ["timestamp"]
    for loc in locations:
        fields.append(f"{loc['id']}_temp")
        fields.append(f"{loc['id']}_hum")

    # 2. Check which date ranges need to be queried from Home Assistant
    # Past months that already exist locally are kept as-is (NEVER re-queried)
    needed_query_start: Optional[datetime.datetime] = None

    # Check if any past months are missing on disk
    cur_m = datetime.datetime(start_date.year, start_date.month, 1, tzinfo=datetime.timezone.utc)
    while cur_m < datetime.datetime(now.year, now.month, 1, tzinfo=datetime.timezone.utc):
        past_key = cur_m.strftime("%Y-%m")
        if past_key not in cached_monthly:
            logger.info(f"Missing local archive for past month {past_key}. Will query HA LTS.")
            if needed_query_start is None or cur_m < needed_query_start:
                needed_query_start = start_date
        else:
            logger.debug(f"Past month {past_key} is cached locally ({len(cached_monthly[past_key]['series'])} points).")
        # Advance 1 month
        next_year = cur_m.year + (cur_m.month // 12)
        next_month = (cur_m.month % 12) + 1
        cur_m = datetime.datetime(next_year, next_month, 1, tzinfo=datetime.timezone.utc)

    # Check current month cache state
    if now_m_key in cached_monthly:
        curr_series = cached_monthly[now_m_key].get("series", [])
        if curr_series:
            latest_ts = curr_series[-1][0]
            age_sec = now.timestamp() - latest_ts
            if age_sec < 3600:
                logger.info(f"Current month {now_m_key} is up-to-date in cache ({age_sec / 60:.1f} min old). Skipping HA query.")
            else:
                last_dt = datetime.datetime.fromtimestamp(latest_ts, datetime.timezone.utc)
                if needed_query_start is None or last_dt < needed_query_start:
                    needed_query_start = last_dt
                logger.info(f"Current month {now_m_key} needs incremental update from {last_dt} ({age_sec / 3600:.1f} hrs).")
        else:
            first_of_month = datetime.datetime(now.year, now.month, 1, tzinfo=datetime.timezone.utc)
            if needed_query_start is None or first_of_month < needed_query_start:
                needed_query_start = first_of_month
    else:
        first_of_month = datetime.datetime(now.year, now.month, 1, tzinfo=datetime.timezone.utc)
        if needed_query_start is None or first_of_month < needed_query_start:
            needed_query_start = first_of_month

    # 3. Query HA LTS only if necessary
    if needed_query_start is not None:
        logger.info(f"Querying Home Assistant LTS WebSocket starting from {needed_query_start.isoformat()}...")
        stats_data = client.get_statistics(entity_ids, needed_query_start, end_time=now, period="hour")

        # Map each entity to timestamp -> value
        entity_pts: Dict[str, Dict[int, float]] = {}
        for eid, pts in stats_data.items():
            m = {}
            for p in pts:
                start_ms = p.get("start", 0)
                sec_ts = int(start_ms / 1000)
                val = p.get("mean")
                if val is None:
                    val = p.get("state")
                if val is not None:
                    try:
                        m[sec_ts] = round(float(val), 1)
                    except (ValueError, TypeError):
                        pass
            entity_pts[eid] = m

        fetched_timestamps = sorted(set(ts for m in entity_pts.values() for ts in m.keys()))

        # Group new points by month
        new_by_month: Dict[str, List[List[Any]]] = {}
        for ts in fetched_timestamps:
            dt = datetime.datetime.fromtimestamp(ts, datetime.timezone.utc)
            m_key = dt.strftime("%Y-%m")
            if m_key not in new_by_month:
                new_by_month[m_key] = []

            row = [ts]
            for loc_id, t_eid, h_eid in loc_entities:
                t_val = entity_pts.get(t_eid, {}).get(ts)
                h_val = entity_pts.get(h_eid, {}).get(ts)
                row.append(t_val)
                row.append(h_val)
            new_by_month[m_key].append(row)

        # Merge newly fetched rows into cached_monthly
        for m_key, new_rows in new_by_month.items():
            if m_key in cached_monthly:
                existing_dict = {r[0]: r for r in cached_monthly[m_key].get("series", [])}
                for r in new_rows:
                    existing_dict[r[0]] = r
                merged_series = [existing_dict[t] for t in sorted(existing_dict.keys())]
                cached_monthly[m_key] = {
                    "period": m_key,
                    "step_seconds": 3600,
                    "fields": fields,
                    "series": merged_series,
                }
            else:
                cached_monthly[m_key] = {
                    "period": m_key,
                    "step_seconds": 3600,
                    "fields": fields,
                    "series": new_rows,
                }
    else:
        logger.info("All monthly archives are fully cached on disk. Zero LTS queries to Home Assistant made.")

    # 4. Construct metadata array for manifest.json & months.json
    months_meta: List[Dict[str, Any]] = []
    for m_key in sorted(cached_monthly.keys(), reverse=True):
        m_rows = cached_monthly[m_key].get("series", [])
        year, month_num = int(m_key[:4]), int(m_key[5:7])
        m_name = LATVIAN_MONTH_NAMES.get(month_num, m_key)
        is_curr = (m_key == now_m_key)
        short_label = "Šis mēnesis" if is_curr else m_name
        full_label = f"Šis mēnesis ({m_name.lower()})" if is_curr else f"{year}. gada {m_name.lower()}"

        months_meta.append({
            "id": m_key,
            "name": short_label,
            "month_name": m_name,
            "label": full_label,
            "year": year,
            "month": month_num,
            "is_current": is_curr,
            "file": f"history/history-{m_key}.json",
            "points": len(m_rows),
            "start_time": m_rows[0][0] if m_rows else None,
            "end_time": m_rows[-1][0] if m_rows else None,
        })

    logger.info(f"Available monthly archives: {[m['id'] for m in months_meta]}")
    return cached_monthly, months_meta


def generate_mock_data(
    locations: List[Dict[str, Any]],
    days: int = 7,
    start_date_str: str = "2026-07-15",
) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Dict[str, Any]], List[Dict[str, Any]]]:
    """Generates authentic diurnal climate curves for 6 sensors for offline testing."""
    now = datetime.datetime.now(datetime.timezone.utc)
    step_seconds = 300
    total_steps = int((days * 86400) / step_seconds)
    start_ts = int(now.timestamp()) - (total_steps * step_seconds)

    fields = ["timestamp"]
    for loc in locations:
        fields.append(f"{loc['id']}_temp")
        fields.append(f"{loc['id']}_hum")

    series_data = []
    baselines = {
        "maja": {"temp_base": 21.5, "temp_amp": 1.2, "hum_base": 50.0, "hum_amp": 5.0},
        "pirts": {"temp_base": 19.8, "temp_amp": 2.0, "hum_base": 58.0, "hum_amp": 8.0},
        "ardurvju": {"temp_base": 14.5, "temp_amp": 6.5, "hum_base": 75.0, "hum_amp": 18.0},
    }

    last_values: Dict[str, float] = {}

    for i in range(total_steps + 1):
        ts = start_ts + (i * step_seconds)
        dt = datetime.datetime.fromtimestamp(ts, datetime.timezone.utc)
        hour = dt.hour + (dt.minute / 60.0)

        row = [ts]
        for loc in locations:
            lid = loc["id"]
            cfg = baselines.get(lid, baselines["maja"])

            solar_phase = (hour - 14.0) * (2.0 * math.pi / 24.0)
            solar_temp = math.cos(solar_phase)
            noise_temp = 0.15 * math.sin(i * 0.1) + 0.1 * math.cos(i * 0.03)
            noise_hum = 0.5 * math.sin(i * 0.08)

            t_val = round(cfg["temp_base"] + (cfg["temp_amp"] * solar_temp) + noise_temp, 2)
            h_val = round(min(98.0, max(25.0, cfg["hum_base"] - (cfg["hum_amp"] * solar_temp) + noise_hum)), 1)

            row.append(t_val)
            row.append(h_val)
            last_values[f"{lid}_temp"] = t_val
            last_values[f"{lid}_hum"] = h_val

        series_data.append(row)

    latest_locations = []
    last_24h_series = series_data[-288:] if len(series_data) >= 288 else series_data

    for idx, loc in enumerate(locations):
        lid = loc["id"]
        t_col = 1 + (idx * 2)
        h_col = 2 + (idx * 2)

        t_24h = [r[t_col] for r in last_24h_series if r[t_col] is not None]
        h_24h = [r[h_col] for r in last_24h_series if r[h_col] is not None]

        curr_temp = last_values[f"{lid}_temp"]
        curr_hum = last_values[f"{lid}_hum"]
        past_temp = last_24h_series[-24][t_col] if len(last_24h_series) >= 24 else curr_temp
        past_hum = last_24h_series[-24][h_col] if len(last_24h_series) >= 24 else curr_hum

        latest_locations.append({
            "id": lid,
            "name": loc["name"],
            "description": loc.get("description", ""),
            "icon": loc.get("icon", "thermostat"),
            "temperature": {
                "entity_id": loc["temperature"]["entity_id"],
                "value": curr_temp,
                "unit": loc["temperature"].get("unit", "°C"),
                "min_24h": min(t_24h) if t_24h else curr_temp,
                "max_24h": max(t_24h) if t_24h else curr_temp,
                "avg_24h": round(sum(t_24h) / len(t_24h), 2) if t_24h else curr_temp,
                "trend": calculate_trend(curr_temp, past_temp, 0.2),
                "comfort_min": loc["temperature"].get("comfort_min"),
                "comfort_max": loc["temperature"].get("comfort_max"),
                "last_changed": now.isoformat(),
            },
            "humidity": {
                "entity_id": loc["humidity"]["entity_id"],
                "value": curr_hum,
                "unit": loc["humidity"].get("unit", "%"),
                "min_24h": min(h_24h) if h_24h else curr_hum,
                "max_24h": max(h_24h) if h_24h else curr_hum,
                "avg_24h": round(sum(h_24h) / len(h_24h), 1) if h_24h else curr_hum,
                "trend": calculate_trend(curr_hum, past_hum, 1.0),
                "comfort": calculate_humidity_comfort(curr_hum),
                "comfort_min": loc["humidity"].get("comfort_min"),
                "comfort_max": loc["humidity"].get("comfort_max"),
                "last_changed": now.isoformat(),
            },
        })

    latest_payload = {
        "generated_at": now.isoformat(),
        "total_sensors": len(locations) * 2,
        "locations": latest_locations,
    }

    recent_history_payload = {
        "generated_at": now.isoformat(),
        "start_time": start_ts,
        "end_time": int(now.timestamp()),
        "step_seconds": step_seconds,
        "fields": fields,
        "series": series_data,
    }

    # Generate mock monthly archives back to start_date_str
    start_dt = datetime.datetime.fromisoformat(start_date_str).replace(tzinfo=datetime.timezone.utc)
    curr_hourly_ts = int(start_dt.timestamp())
    now_ts = int(now.timestamp())

    month_buckets: Dict[str, List[List[Any]]] = {}
    while curr_hourly_ts <= now_ts:
        dt = datetime.datetime.fromtimestamp(curr_hourly_ts, datetime.timezone.utc)
        m_key = dt.strftime("%Y-%m")
        if m_key not in month_buckets:
            month_buckets[m_key] = []

        month_temp_offset = {7: 4.0, 8: 3.0, 9: 0.0}.get(dt.month, 0.0)
        solar_phase = (dt.hour - 14.0) * (2.0 * math.pi / 24.0)
        solar_temp = math.cos(solar_phase)

        row = [curr_hourly_ts]
        for loc in locations:
            lid = loc["id"]
            cfg = baselines.get(lid, baselines["maja"])
            t_val = round(cfg["temp_base"] + month_temp_offset + (cfg["temp_amp"] * solar_temp), 1)
            h_val = round(min(98.0, max(25.0, cfg["hum_base"] - (cfg["hum_amp"] * solar_temp))), 1)
            row.append(t_val)
            row.append(h_val)

        month_buckets[m_key].append(row)
        curr_hourly_ts += 3600

    now_m_key = now.strftime("%Y-%m")
    monthly_payloads: Dict[str, Dict[str, Any]] = {}
    months_meta: List[Dict[str, Any]] = []

    for m_key in sorted(month_buckets.keys(), reverse=True):
        m_rows = month_buckets[m_key]
        monthly_payloads[m_key] = {
            "period": m_key,
            "step_seconds": 3600,
            "fields": fields,
            "series": m_rows,
        }

        year, month_num = int(m_key[:4]), int(m_key[5:7])
        m_name = LATVIAN_MONTH_NAMES.get(month_num, m_key)
        is_curr = (m_key == now_m_key)
        short_label = "Šis mēnesis" if is_curr else m_name
        full_label = f"Šis mēnesis ({m_name.lower()})" if is_curr else f"{year}. gada {m_name.lower()}"

        months_meta.append({
            "id": m_key,
            "name": short_label,
            "month_name": m_name,
            "label": full_label,
            "year": year,
            "month": month_num,
            "is_current": is_curr,
            "file": f"history/history-{m_key}.json",
            "points": len(m_rows),
            "start_time": m_rows[0][0] if m_rows else None,
            "end_time": m_rows[-1][0] if m_rows else None,
        })

    return latest_payload, recent_history_payload, monthly_payloads, months_meta


def process_real_ha_data(
    client: HomeAssistantClient,
    locations: List[Dict[str, Any]],
    days: int = 7,
    step_seconds: int = 300,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Fetches real sensor states and recent history from Home Assistant REST API."""
    now = datetime.datetime.now(datetime.timezone.utc)
    start_time = now - datetime.timedelta(days=days)

    entity_ids = []
    for loc in locations:
        t_eid = loc["temperature"]["entity_id"]
        h_eid = loc["humidity"]["entity_id"]
        entity_ids.extend([t_eid, h_eid])

    logger.info(f"Querying Home Assistant recent history for {len(entity_ids)} entities over last {days} days...")
    raw_history = client.get_history(entity_ids, start_time, now)

    current_states: Dict[str, Any] = {}
    for eid in entity_ids:
        state_obj = client.get_state(eid)
        if state_obj:
            current_states[eid] = state_obj

    total_steps = int((days * 86400) / step_seconds)
    start_ts = int(now.timestamp()) - (total_steps * step_seconds)
    time_grid = [start_ts + (i * step_seconds) for i in range(total_steps + 1)]

    resampled_series: Dict[str, List[Optional[float]]] = {}
    for eid in entity_ids:
        records = raw_history.get(eid, [])
        parsed_points: List[Tuple[float, float]] = []
        for r in records:
            last_changed = r.get("last_changed") or r.get("last_updated")
            if not last_changed:
                continue
            try:
                clean_iso = last_changed.replace("Z", "+00:00")
                dt = datetime.datetime.fromisoformat(clean_iso)
                ts = dt.timestamp()
                val = parse_float_state(r.get("state"))
                if val is not None:
                    parsed_points.append((ts, val))
            except Exception:
                continue

        parsed_points.sort(key=lambda x: x[0])

        grid_values: List[Optional[float]] = []
        point_idx = 0
        last_val: Optional[float] = None
        for g_ts in time_grid:
            while point_idx < len(parsed_points) and parsed_points[point_idx][0] <= g_ts:
                last_val = parsed_points[point_idx][1]
                point_idx += 1
            grid_values.append(last_val)

        if grid_values and grid_values[-1] is None and eid in current_states:
            grid_values[-1] = parse_float_state(current_states[eid].get("state"))

        resampled_series[eid] = grid_values

    fields = ["timestamp"]
    for loc in locations:
        fields.append(f"{loc['id']}_temp")
        fields.append(f"{loc['id']}_hum")

    series_data = []
    for step_i, g_ts in enumerate(time_grid):
        row = [g_ts]
        for loc in locations:
            t_eid = loc["temperature"]["entity_id"]
            h_eid = loc["humidity"]["entity_id"]
            row.append(resampled_series.get(t_eid, [None] * len(time_grid))[step_i])
            row.append(resampled_series.get(h_eid, [None] * len(time_grid))[step_i])
        series_data.append(row)

    latest_locations = []
    slice_24h = series_data[-288:] if len(series_data) >= 288 else series_data

    for idx, loc in enumerate(locations):
        lid = loc["id"]
        t_eid = loc["temperature"]["entity_id"]
        h_eid = loc["humidity"]["entity_id"]

        t_col = 1 + (idx * 2)
        h_col = 2 + (idx * 2)

        t_24h = [r[t_col] for r in slice_24h if r[t_col] is not None]
        h_24h = [r[h_col] for r in slice_24h if r[h_col] is not None]

        curr_t = parse_float_state(current_states.get(t_eid, {}).get("state"))
        if curr_t is None and t_24h:
            curr_t = t_24h[-1]

        curr_h = parse_float_state(current_states.get(h_eid, {}).get("state"))
        if curr_h is None and h_24h:
            curr_h = h_24h[-1]

        past_t = slice_24h[-24][t_col] if len(slice_24h) >= 24 else curr_t
        past_h = slice_24h[-24][h_col] if len(slice_24h) >= 24 else curr_h

        t_state = current_states.get(t_eid, {})
        h_state = current_states.get(h_eid, {})

        latest_locations.append({
            "id": lid,
            "name": loc["name"],
            "description": loc.get("description", ""),
            "icon": loc.get("icon", "thermostat"),
            "temperature": {
                "entity_id": t_eid,
                "value": curr_t,
                "unit": loc["temperature"].get("unit", "°C"),
                "min_24h": min(t_24h) if t_24h else curr_t,
                "max_24h": max(t_24h) if t_24h else curr_t,
                "avg_24h": round(sum(t_24h) / len(t_24h), 2) if t_24h else curr_t,
                "trend": calculate_trend(curr_t, past_t, 0.2),
                "comfort_min": loc["temperature"].get("comfort_min"),
                "comfort_max": loc["temperature"].get("comfort_max"),
                "last_changed": t_state.get("last_changed", now.isoformat()),
            },
            "humidity": {
                "entity_id": h_eid,
                "value": curr_h,
                "unit": loc["humidity"].get("unit", "%"),
                "min_24h": min(h_24h) if h_24h else curr_h,
                "max_24h": max(h_24h) if h_24h else curr_h,
                "avg_24h": round(sum(h_24h) / len(h_24h), 1) if h_24h else curr_h,
                "trend": calculate_trend(curr_h, past_h, 1.0),
                "comfort": calculate_humidity_comfort(curr_h),
                "comfort_min": loc["humidity"].get("comfort_min"),
                "comfort_max": loc["humidity"].get("comfort_max"),
                "last_changed": h_state.get("last_changed", now.isoformat()),
            },
        })

    latest_payload = {
        "generated_at": now.isoformat(),
        "total_sensors": len(locations) * 2,
        "locations": latest_locations,
    }

    recent_history_payload = {
        "generated_at": now.isoformat(),
        "start_time": start_ts,
        "end_time": int(now.timestamp()),
        "step_seconds": step_seconds,
        "fields": fields,
        "series": series_data,
    }

    return latest_payload, recent_history_payload


def write_export_files(
    output_dir: Path,
    latest_payload: Dict[str, Any],
    recent_history_payload: Dict[str, Any],
    monthly_payloads: Dict[str, Dict[str, Any]],
    months_meta: List[Dict[str, Any]],
    locations: List[Dict[str, Any]],
) -> List[Path]:
    """Writes JSON payloads to target directory and returns list of created files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    history_dir = output_dir / "history"
    history_dir.mkdir(parents=True, exist_ok=True)

    written_files: List[Path] = []

    # 1. latest.json
    latest_file = output_dir / "latest.json"
    with open(latest_file, "w", encoding="utf-8") as f:
        json.dump(latest_payload, f, indent=2, ensure_ascii=False)
    written_files.append(latest_file)

    # 2. history-recent.json (compact)
    recent_file = output_dir / "history-recent.json"
    with open(recent_file, "w", encoding="utf-8") as f:
        json.dump(recent_history_payload, f, separators=(",", ":"), ensure_ascii=False)
    written_files.append(recent_file)

    # 3. Monthly archives
    for month_key, month_payload in monthly_payloads.items():
        arch_file = history_dir / f"history-{month_key}.json"
        with open(arch_file, "w", encoding="utf-8") as f:
            json.dump(month_payload, f, separators=(",", ":"), ensure_ascii=False)
        written_files.append(arch_file)

    # 4. manifest.json
    manifest_payload = {
        "version": "1.0",
        "generated_at": latest_payload["generated_at"],
        "sensors": [
            {
                "location_id": loc["id"],
                "location_name": loc["name"],
                "icon": loc.get("icon", "thermostat"),
                "temp_entity": loc["temperature"]["entity_id"],
                "hum_entity": loc["humidity"]["entity_id"],
            }
            for loc in locations
        ],
        "recent_file": "history-recent.json",
        "months": months_meta,
        "archives": months_meta,
    }
    manifest_file = output_dir / "manifest.json"
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest_payload, f, indent=2, ensure_ascii=False)
    written_files.append(manifest_file)

    # 5. months.json (dedicated endpoint listing valid months for dynamic UI)
    months_file = output_dir / "months.json"
    with open(months_file, "w", encoding="utf-8") as f:
        json.dump(months_meta, f, indent=2, ensure_ascii=False)
    written_files.append(months_file)

    logger.info(f"Successfully updated {len(written_files)} export files in {output_dir}")
    return written_files


def run_rsync(rsync_cfg: Dict[str, Any], local_dir: Path) -> bool:
    """Executes rsync to push data files to the Scaleway server."""
    remote_host = rsync_cfg.get("remote_host", "aigarius.com")
    remote_user = rsync_cfg.get("remote_user", "debian")
    remote_port = rsync_cfg.get("remote_port", 22)
    remote_dir = rsync_cfg.get("remote_dir", "/var/www/pidiki_data/").rstrip("/") + "/"
    ssh_key = rsync_cfg.get("ssh_key_path")
    extra_flags = rsync_cfg.get("extra_flags", "-avz --delete").split()

    src_path = str(local_dir.resolve()).rstrip("/") + "/"
    dest_spec = f"{remote_user}@{remote_host}:{remote_dir}"

    ssh_cmd = f"ssh -p {remote_port}"
    if ssh_key:
        ssh_key_expanded = str(Path(ssh_key).expanduser())
        ssh_cmd += f" -i {ssh_key_expanded}"

    cmd = ["rsync"] + extra_flags + ["-e", ssh_cmd, src_path, dest_spec]
    logger.info(f"Running rsync: {' '.join(cmd)}")

    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        logger.info(f"Rsync completed successfully:\n{res.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Rsync failed with code {e.returncode}:\n{e.stderr}")
        return False
    except FileNotFoundError:
        logger.error("rsync command not found in PATH")
        return False


def main():
    parser = argparse.ArgumentParser(description="Export Home Assistant climate data for Pidiki static dashboard")
    parser.add_argument("--config", "-c", type=Path, default=Path(__file__).parent / "config.yaml",
                        help="Path to YAML configuration file")
    parser.add_argument("--output-dir", "-o", type=Path, default=None,
                        help="Override destination directory for generated files")
    parser.add_argument("--mock", action="store_true",
                        help="Generate synthetic realistic test data without querying Home Assistant")
    parser.add_argument("--days", "-d", type=int, default=7,
                        help="Number of days of recent history to include (default: 7)")
    parser.add_argument("--rsync", action="store_true",
                        help="Execute rsync push to Scaleway server after generation")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Enable verbose debug logging")

    args = parser.parse_args()
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    config = load_config(args.config)
    locations = config.get("locations", [])
    if not locations:
        logger.error("No locations/sensors defined in configuration.")
        sys.exit(1)

    output_dir = args.output_dir or Path(config.get("export", {}).get("output_dir", "./data_output"))
    history_start = config.get("export", {}).get("history_start_date", "2026-07-15")

    if args.mock:
        logger.info("Mock mode enabled: generating synthetic climate history...")
        latest_payload, recent_payload, monthly_payloads, months_meta = generate_mock_data(
            locations, days=args.days, start_date_str=history_start
        )
    else:
        ha_cfg = config.get("home_assistant", {})
        url = ha_cfg.get("url")
        token = ha_cfg.get("token")
        if not url or not token or token.startswith("PASTE_YOUR"):
            logger.error("Home Assistant URL or Token is missing in config.yaml. Use --mock for offline testing.")
            sys.exit(1)

        client = HomeAssistantClient(url, token, timeout=ha_cfg.get("timeout", 30))
        latest_payload, recent_payload = process_real_ha_data(
            client=client,
            locations=locations,
            days=args.days,
            step_seconds=config.get("export", {}).get("recent_interval_seconds", 300),
        )
        monthly_payloads, months_meta = fetch_and_process_lts_history(
            client=client,
            locations=locations,
            output_dir=output_dir,
            start_date_str=history_start,
        )

    # Write files
    written_files = write_export_files(
        output_dir=output_dir,
        latest_payload=latest_payload,
        recent_history_payload=recent_payload,
        monthly_payloads=monthly_payloads,
        months_meta=months_meta,
        locations=locations,
    )

    should_rsync = args.rsync or config.get("rsync", {}).get("enabled", False)
    if should_rsync:
        run_rsync(config.get("rsync", {}), output_dir)


if __name__ == "__main__":
    main()
