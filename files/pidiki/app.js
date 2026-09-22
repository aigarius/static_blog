/**
 * Pidiki Climate Dashboard - Client Application
 * Optimized for Senior Users (70+ with non-perfect eyesight):
 * - Large, high-contrast typography
 * - Clean layout without statistical clutter
 * - Thick, high-contrast chart lines
 * - Full accessibility on 1080p laptop and iPhone
 * - Fully dynamic monthly archives (recent buttons + historical dropdown)
 */

// Application State
const state = {
  latest: null,
  manifest: null,
  recentHistory: null,
  monthCache: {},             // '2026-09': payload, '2026-08': payload, ...
  activeRange: '24h',        // '24h' | '7d' | 'month'
  activeMonthId: null,       // e.g. '2026-09'
  activeMetric: 'all',       // 'all' | 'temp' | 'hum'
  activeLocations: new Set(['maja', 'pirts', 'ardurvju']),
  autoRefresh: true,
  autoRefreshInterval: null,
  relativeTimerInterval: null,
  chartInstance: null,
  lastSyncDate: null,
};

// Area-grouped high-contrast color families:
// Māja = Warm Orange/Amber family
// Pirts = Cool Blue/Cyan family
// Ārdurvis = Purple/Lilac family
const SENSOR_STYLES = {
  maja: {
    temp: { label: 'Māja — Temp.', color: '#ff6b4a', pointStyle: 'circle', yAxisID: 'yTemp' },
    hum:  { label: 'Māja — Mitr.',  color: '#ffa94d', pointStyle: 'rectRounded', yAxisID: 'yHum'  },
  },
  pirts: {
    temp: { label: 'Pirts — Temp.', color: '#339af0', pointStyle: 'circle', yAxisID: 'yTemp' },
    hum:  { label: 'Pirts — Mitr.',  color: '#3bc9db', pointStyle: 'rectRounded', yAxisID: 'yHum'  },
  },
  ardurvju: {
    temp: { label: 'Ārdurvis — Temp.', color: '#cc5de8', pointStyle: 'circle', yAxisID: 'yTemp' },
    hum:  { label: 'Ārdurvis — Mitr.',  color: '#e599f7', pointStyle: 'rectRounded', yAxisID: 'yHum'  },
  },
};

const COMFORT_LABELS = {
  ideal: 'Optimāls',
  dry: 'Sauss',
  humid: 'Mitrs',
  unknown: 'Nenoteikts',
};

const TREND_LABELS = {
  rising: 'pieaug',
  falling: 'krītas',
  stable: 'stabili',
};

// DOM Elements
const dom = {
  statusBadge: document.getElementById('statusBadge'),
  statusLabel: document.getElementById('statusLabel'),
  pulseDot: document.getElementById('pulseDot'),
  lastUpdatedTime: document.getElementById('lastUpdatedTime'),
  refreshBtn: document.getElementById('refreshBtn'),
  refreshIcon: document.getElementById('refreshIcon'),
  alertBanner: document.getElementById('alertBanner'),
  alertMessage: document.getElementById('alertMessage'),
  dismissAlertBtn: document.getElementById('dismissAlertBtn'),
  locationsGrid: document.getElementById('locationsGrid'),
  chartCanvas: document.getElementById('climateChart'),
  chartLoadingOverlay: document.getElementById('chartLoadingOverlay'),
  rangePicker: document.getElementById('rangePicker'),
  monthSelect: document.getElementById('monthSelect'),
  metricButtons: document.querySelectorAll('.metric-filter-btn'),
  locationChips: document.querySelectorAll('.loc-filter-chip'),
  analyticsTableBody: document.getElementById('analyticsTableBody'),
};

// Utilities
function formatRelativeTime(date) {
  if (!date) return '--';
  const diffSec = Math.floor((Date.now() - date.getTime()) / 1000);
  if (diffSec < 15) return 'tikko';
  if (diffSec < 60) return `pirms ${diffSec} s`;
  const diffMin = Math.floor(diffSec / 60);
  if (diffMin < 60) return `pirms ${diffMin} min.`;
  const diffHr = Math.floor(diffMin / 60);
  return `pirms ${diffHr} st.`;
}

function showAlert(message) {
  dom.alertMessage.textContent = message;
  dom.alertBanner.classList.remove('hidden');
}

function hideAlert() {
  dom.alertBanner.classList.add('hidden');
}

function setOnlineStatus(online, label) {
  if (online) {
    dom.statusBadge.classList.add('online');
    dom.statusLabel.textContent = label || 'TIEŠRAIDE';
  } else {
    dom.statusBadge.classList.remove('online');
    dom.statusLabel.textContent = label || 'BEZSAISTE';
  }
}

// Data Fetching
async function fetchJSON(url) {
  const cacheBuster = `_t=${Date.now()}`;
  const sep = url.includes('?') ? '&' : '?';
  const fullUrl = `${url}${sep}${cacheBuster}`;

  const res = await fetch(fullUrl, { cache: 'no-store' });
  if (!res.ok) {
    throw new Error(`Neizdevās ielādēt ${url} (HTTP ${res.status})`);
  }
  return await res.json();
}

async function loadLatestData() {
  try {
    const data = await fetchJSON('./data/latest.json');
    state.latest = data;
    if (data.generated_at) {
      state.lastSyncDate = new Date(data.generated_at);
      dom.lastUpdatedTime.textContent = `Atjaunināts: ${formatRelativeTime(state.lastSyncDate)}`;
    }
    setOnlineStatus(true, 'TIEŠRAIDE');
    renderLocationsGrid(data.locations || []);
    hideAlert();
  } catch (err) {
    console.error('Kļūda, ielādējot latest.json:', err);
    setOnlineStatus(false, 'NOVECOJIS');
    showAlert(`Nevar pieslēgties reāllaika sensoru plūsmai. Tiek rādīti saglabātie dati.`);
  }
}

async function loadManifest() {
  try {
    const manifest = await fetchJSON('./data/manifest.json');
    state.manifest = manifest;
    if (manifest.months && manifest.months.length > 0) {
      renderDynamicControls(manifest.months);
    }
  } catch (err) {
    console.warn('Nevarēja ielādēt manifest.json:', err);
  }
}

async function loadRecentHistory() {
  try {
    dom.chartLoadingOverlay.classList.remove('hidden');
    const data = await fetchJSON('./data/history-recent.json');
    state.recentHistory = data;
    updateChartAndAnalytics();
  } catch (err) {
    console.error('Kļūda, ielādējot history-recent.json:', err);
    showAlert(`Neizdevās ielādēt vēstures datus.`);
  } finally {
    dom.chartLoadingOverlay.classList.add('hidden');
  }
}

// Month & Range Selection
async function selectMonth(monthId) {
  state.activeRange = 'month';
  state.activeMonthId = monthId;

  updateControlSelectionUI();

  if (!state.monthCache[monthId]) {
    dom.chartLoadingOverlay.classList.remove('hidden');
    try {
      const monthData = await fetchJSON(`./data/history/history-${monthId}.json`);
      state.monthCache[monthId] = monthData;
    } catch (err) {
      console.error(`Kļūda, ielādējot history-${monthId}.json:`, err);
      showAlert(`Neizdevās ielādēt mēneša datus (${monthId}).`);
      return;
    } finally {
      dom.chartLoadingOverlay.classList.add('hidden');
    }
  }

  updateChartAndAnalytics();
}

async function selectRecentRange(range) {
  state.activeRange = range;
  state.activeMonthId = null;

  updateControlSelectionUI();

  if (!state.recentHistory) {
    await loadRecentHistory();
  } else {
    updateChartAndAnalytics();
  }
}

// Synchronize UI active styling across quick buttons and dropdown
function updateControlSelectionUI() {
  if (dom.rangePicker) {
    const btns = dom.rangePicker.querySelectorAll('.range-btn');
    let matchedQuickBtn = false;

    btns.forEach((b) => {
      const isActive =
        (b.dataset.range === 'month' && state.activeRange === 'month' && b.dataset.month === state.activeMonthId) ||
        (b.dataset.range !== 'month' && state.activeRange === b.dataset.range);

      if (isActive) {
        b.classList.add('active');
        matchedQuickBtn = true;
      } else {
        b.classList.remove('active');
      }
    });

    if (dom.monthSelect) {
      if (state.activeRange === 'month' && state.activeMonthId) {
        if (!matchedQuickBtn) {
          dom.monthSelect.value = state.activeMonthId;
          dom.monthSelect.classList.add('active');
        } else {
          dom.monthSelect.value = '';
          dom.monthSelect.classList.remove('active');
        }
      } else {
        dom.monthSelect.value = '';
        dom.monthSelect.classList.remove('active');
      }
    }
  }
}

// Render Dynamic Controls: historical dropdown, up to 3 recent month buttons, 7d, 24h
// Visual order: Historical data to the left, recent periods to the right
function renderDynamicControls(months) {
  if (!dom.rangePicker) return;

  // 1. Populate Range & Recent Month Buttons
  dom.rangePicker.innerHTML = '';

  const buttonsDef = [];

  // Up to 3 most recent months get dedicated quick buttons (oldest -> newest)
  const recentMonths = (months || []).slice(0, 3).reverse();
  recentMonths.forEach((m) => {
    buttonsDef.push({
      label: m.name || m.month_name || m.label,
      title: m.label || m.name,
      range: 'month',
      monthId: m.id,
    });
  });

  // Recent periods to the right
  buttonsDef.push(
    { label: '7 dienas', range: '7d', monthId: null },
    { label: '24 stundas', range: '24h', monthId: null }
  );

  buttonsDef.forEach((def) => {
    const btn = document.createElement('button');
    btn.className = 'range-btn';
    btn.textContent = def.label;
    if (def.title) btn.title = def.title;
    btn.dataset.range = def.range;
    if (def.monthId) btn.dataset.month = def.monthId;

    btn.addEventListener('click', async () => {
      if (def.range === 'month') {
        await selectMonth(def.monthId);
      } else {
        await selectRecentRange(def.range);
      }
    });

    dom.rangePicker.appendChild(btn);
  });

  // 2. Populate Full Historical Month Dropdown
  if (dom.monthSelect) {
    dom.monthSelect.innerHTML = '<option value="">Visi mēneši...</option>';
    (months || []).forEach((m) => {
      const opt = document.createElement('option');
      opt.value = m.id;
      opt.textContent = m.label || `${m.year}. gada ${m.month_name}`;
      dom.monthSelect.appendChild(opt);
    });
  }

  updateControlSelectionUI();
}

// Render Uncluttered, Senior-Accessible Location Cards
function renderLocationsGrid(locations) {
  if (!locations || locations.length === 0) return;

  dom.locationsGrid.innerHTML = '';

  locations.forEach((loc) => {
    const card = document.createElement('div');
    card.className = 'location-card';
    card.id = `card-${loc.id}`;

    const temp = loc.temperature || {};
    const hum = loc.humidity || {};

    const tempTrendRaw = temp.trend || 'stable';
    const humTrendRaw = hum.trend || 'stable';

    const tempTrendText = TREND_LABELS[tempTrendRaw] || tempTrendRaw;
    const humTrendText = TREND_LABELS[humTrendRaw] || humTrendRaw;

    const tempTrendIcon = tempTrendRaw === 'rising' ? '▲' : tempTrendRaw === 'falling' ? '▼' : '━';
    const humTrendIcon = humTrendRaw === 'rising' ? '▲' : humTrendRaw === 'falling' ? '▼' : '━';

    const tempValStr = temp.value !== null && temp.value !== undefined ? Number(temp.value).toFixed(1) : '--';
    const humValStr = hum.value !== null && hum.value !== undefined ? Math.round(Number(hum.value)) : '--';

    const comfortRaw = hum.comfort || 'ideal';
    const comfortLabel = COMFORT_LABELS[comfortRaw] || comfortRaw;

    const locStyle = SENSOR_STYLES[loc.id] || {};
    const tempColor = locStyle.temp ? locStyle.temp.color : '#ff6b4a';
    const humColor = locStyle.hum ? locStyle.hum.color : '#ffa94d';

    card.innerHTML = `
      <div class="card-header" style="border-top: 4px solid ${tempColor}; padding-top: 10px; margin-top: -8px;">
        <h3 class="card-title">${loc.name}</h3>
        <span class="card-desc">${loc.description || ''}</span>
      </div>

      <div class="metrics-row">
        <!-- Giant Temperature Block -->
        <div class="metric-block temp">
          <div class="metric-header">
            <span class="metric-label" style="color: ${tempColor};">Temperatūra</span>
            <span class="trend-badge" style="color: ${tempColor}; background: ${tempColor}22; border: 1.5px solid ${tempColor}55;" title="Tendence: ${tempTrendText}" aria-label="Tendence: ${tempTrendText}">
              ${tempTrendIcon}
            </span>
          </div>
          <div class="metric-value-row">
            <span class="metric-value" style="color: ${tempColor}; text-shadow: 0 0 16px ${tempColor}35;">${tempValStr}</span>
            <span class="metric-unit">${temp.unit || '°C'}</span>
          </div>
        </div>

        <!-- Giant Humidity Block -->
        <div class="metric-block hum">
          <div class="metric-header">
            <span class="metric-label" style="color: ${humColor};">Mitrums</span>
            <span class="trend-badge" style="color: ${humColor}; background: ${humColor}22; border: 1.5px solid ${humColor}55;" title="Tendence: ${humTrendText}" aria-label="Tendence: ${humTrendText}">
              ${humTrendIcon}
            </span>
          </div>
          <div class="metric-value-row">
            <span class="metric-value" style="color: ${humColor}; text-shadow: 0 0 16px ${humColor}35;">${humValStr}</span>
            <span class="metric-unit">${hum.unit || '%'}</span>
          </div>
          <div class="comfort-badge ${comfortRaw}">${comfortLabel}</div>
        </div>
      </div>
    `;

    dom.locationsGrid.appendChild(card);
  });
}

// Assemble Historical Datasets for Chart.js
function getFilteredSeriesData() {
  if (state.activeRange === 'month' && state.activeMonthId) {
    const monthData = state.monthCache[state.activeMonthId];
    if (!monthData || !monthData.series) return { rows: [], fields: [] };
    return { rows: monthData.series, fields: monthData.fields || [] };
  }

  if (!state.recentHistory || !state.recentHistory.series) return { rows: [], fields: [] };

  const allRows = state.recentHistory.series;
  const fields = state.recentHistory.fields || [];

  if (allRows.length === 0) return { rows: [], fields };

  const lastRow = allRows[allRows.length - 1];
  const maxTs = lastRow[0];

  let rangeSeconds = 86400; // default 24h
  if (state.activeRange === '7d') rangeSeconds = 7 * 86400;

  const minTs = maxTs - rangeSeconds;
  const filteredRows = allRows.filter((row) => row[0] >= minTs);

  return { rows: filteredRows, fields };
}

function initOrUpdateChart() {
  const { rows, fields } = getFilteredSeriesData();
  if (rows.length === 0 || fields.length === 0) return;

  const fieldIndexMap = {};
  fields.forEach((f, idx) => {
    fieldIndexMap[f] = idx;
  });

  const datasets = [];

  ['maja', 'pirts', 'ardurvju'].forEach((locId) => {
    if (!state.activeLocations.has(locId)) return;

    const locStyle = SENSOR_STYLES[locId];
    const tempField = `${locId}_temp`;
    const humField = `${locId}_hum`;

    // 1. Temperature dataset (thick solid line, 4px)
    if (state.activeMetric === 'all' || state.activeMetric === 'temp') {
      const colIdx = fieldIndexMap[tempField];
      if (colIdx !== undefined) {
        const points = rows.map((r) => ({
          x: r[0] * 1000,
          y: r[colIdx],
        }));

        datasets.push({
          label: locStyle.temp.label,
          data: points,
          borderColor: locStyle.temp.color,
          backgroundColor: locStyle.temp.color,
          borderWidth: 4.0, // Thick line for temperature
          borderDash: [],   // Solid line
          fill: false,
          spanGaps: true,   // Seamless line across single missing samples
          pointStyle: locStyle.temp.pointStyle, // Circle
          pointRadius: 0,
          pointHoverRadius: 9,
          pointBackgroundColor: locStyle.temp.color,
          pointBorderColor: locStyle.temp.color, // Color matches line
          pointBorderWidth: 1,
          pointHoverBackgroundColor: locStyle.temp.color,
          pointHoverBorderColor: '#ffffff',
          pointHoverBorderWidth: 2,
          tension: 0.25,
          yAxisID: 'yTemp',
        });
      }
    }

    // 2. Humidity dataset (thinner solid line, 2px - NOT dashed)
    if (state.activeMetric === 'all' || state.activeMetric === 'hum') {
      const colIdx = fieldIndexMap[humField];
      if (colIdx !== undefined) {
        const points = rows.map((r) => ({
          x: r[0] * 1000,
          y: r[colIdx],
        }));

        datasets.push({
          label: locStyle.hum.label,
          data: points,
          borderColor: locStyle.hum.color,
          backgroundColor: locStyle.hum.color,
          borderWidth: 2.0, // Thinner line for humidity as requested
          borderDash: [],   // Solid line (NOT dashed as requested)
          fill: false,
          spanGaps: true,   // Seamless line across single missing samples
          pointStyle: locStyle.hum.pointStyle, // Rounded rectangle
          pointRadius: 0,
          pointHoverRadius: 8,
          pointBackgroundColor: locStyle.hum.color,
          pointBorderColor: locStyle.hum.color, // Color matches line
          pointBorderWidth: 1,
          pointHoverBackgroundColor: locStyle.hum.color,
          pointHoverBorderColor: '#ffffff',
          pointHoverBorderWidth: 2,
          tension: 0.25,
          yAxisID: 'yHum',
        });
      }
    }
  });

  // Calculate dynamic Min/Max for Y-axes
  let tempMin = Infinity, tempMax = -Infinity;
  let humMin = Infinity, humMax = -Infinity;

  datasets.forEach((ds) => {
    ds.data.forEach((p) => {
      if (p.y !== null && p.y !== undefined) {
        if (ds.yAxisID === 'yTemp') {
          if (p.y < tempMin) tempMin = p.y;
          if (p.y > tempMax) tempMax = p.y;
        } else {
          if (p.y < humMin) humMin = p.y;
          if (p.y > humMax) humMax = p.y;
        }
      }
    });
  });

  if (tempMin === Infinity) { tempMin = 10; tempMax = 30; }
  else {
    tempMin = Math.floor(tempMin - 1.5);
    tempMax = Math.ceil(tempMax + 1.5);
  }

  if (humMin === Infinity) { humMin = 0; humMax = 100; }
  else {
    humMin = Math.max(0, Math.floor(humMin - 5));
    humMax = Math.min(100, Math.ceil(humMax + 5));
  }

  const showTempAxis = state.activeMetric === 'all' || state.activeMetric === 'temp';
  const showHumAxis = state.activeMetric === 'all' || state.activeMetric === 'hum';

  const chartConfig = {
    type: 'line',
    data: { datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
        intersect: false,
      },
      animation: {
        duration: 250,
      },
      plugins: {
        legend: {
          display: true,
          position: 'top',
          labels: {
            usePointStyle: true,
            pointStyleWidth: 16,
            boxWidth: 16,
            boxHeight: 16,
            color: '#ffffff',
            font: { family: "'Inter', sans-serif", size: 15, weight: '700' },
            padding: 22,
            generateLabels: function(chart) {
              const original = Chart.defaults.plugins.legend.labels.generateLabels(chart);
              original.forEach(label => {
                const ds = chart.data.datasets[label.datasetIndex];
                if (ds) {
                  label.fillStyle = ds.borderColor;   // Exact line color
                  label.strokeStyle = ds.borderColor; // Exact line color
                  label.lineWidth = 1;
                  label.pointStyle = ds.pointStyle;
                }
              });
              return original;
            }
          },
        },
        tooltip: {
          backgroundColor: '#141c2b',
          titleColor: '#ffffff',
          bodyColor: '#ffffff',
          borderColor: 'rgba(255, 255, 255, 0.4)',
          borderWidth: 1.5,
          padding: 14,
          boxPadding: 8,
          titleFont: { size: 15, weight: '700' },
          bodyFont: { size: 15, weight: '600' },
          usePointStyle: true,
          boxWidth: 12,
          boxHeight: 12,
          callbacks: {
            labelColor: function(ctx) {
              return {
                borderColor: ctx.dataset.borderColor,
                backgroundColor: ctx.dataset.borderColor,
                borderWidth: 1,
                borderRadius: 2,
              };
            },
            title: function (items) {
              if (!items.length) return '';
              const date = new Date(items[0].parsed.x);
              return date.toLocaleString('lv-LV', {
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
              });
            },
            label: function (ctx) {
              const val = ctx.parsed.y;
              const unit = ctx.dataset.yAxisID === 'yTemp' ? '°C' : '%';
              return ` ${ctx.dataset.label}: ${val !== null && val !== undefined ? val.toFixed(1) : '--'} ${unit}`;
            },
          },
        },
      },
      scales: {
        x: {
          type: 'time',
          time: {
            tooltipFormat: 'PPpp',
            displayFormats: {
              hour: 'HH:mm',
              day: 'd. MMM',
              month: 'MMM yyyy',
            },
          },
          grid: {
            color: 'rgba(255, 255, 255, 0.08)',
          },
          ticks: {
            color: '#d0d8e2',
            font: { family: "'Inter', sans-serif", size: 13, weight: '600' },
            maxRotation: 0,
            autoSkip: true,
            maxTicksLimit: 12,
          },
        },
        yTemp: {
          type: 'linear',
          display: showTempAxis,
          position: 'left',
          min: tempMin,
          max: tempMax,
          title: {
            display: true,
            text: 'Temperatūra (°C)',
            color: '#ffffff',
            font: { family: "'Inter', sans-serif", weight: '800', size: 15 },
          },
          grid: {
            color: 'rgba(255, 255, 255, 0.08)',
          },
          ticks: {
            color: '#d0d8e2',
            font: { family: "'Inter', sans-serif", size: 14, weight: '700' },
            callback: (val) => `${val} °C`,
          },
        },
        yHum: {
          type: 'linear',
          display: showHumAxis,
          position: 'right',
          min: humMin,
          max: humMax,
          title: {
            display: true,
            text: 'Relatīvais mitrums (%)',
            color: '#ffffff',
            font: { family: "'Inter', sans-serif", weight: '800', size: 15 },
          },
          grid: {
            drawOnChartArea: false,
          },
          ticks: {
            color: '#d0d8e2',
            font: { family: "'Inter', sans-serif", size: 14, weight: '700' },
            callback: (val) => `${val} %`,
          },
        },
      },
    },
  };

  if (state.chartInstance) {
    state.chartInstance.destroy();
  }

  const ctx = dom.chartCanvas.getContext('2d');
  state.chartInstance = new Chart(ctx, chartConfig);
}

// Collapsible Statistical Summary Table
function updateAnalyticsTable(rows, fields) {
  if (!dom.analyticsTableBody || rows.length === 0 || fields.length === 0) return;

  const fieldIndexMap = {};
  fields.forEach((f, idx) => {
    fieldIndexMap[f] = idx;
  });

  const locNames = {
    maja: 'Māja',
    pirts: 'Pirts',
    ardurvju: 'Ārdurvis',
  };

  let html = '';

  ['maja', 'pirts', 'ardurvju'].forEach((locId) => {
    if (!state.activeLocations.has(locId)) return;

    const locName = locNames[locId];
    const locStyle = SENSOR_STYLES[locId] || {};
    const tempColor = locStyle.temp ? locStyle.temp.color : '#ff6b4a';
    const humColor = locStyle.hum ? locStyle.hum.color : '#ffa94d';

    // Temperature Row
    if (state.activeMetric === 'all' || state.activeMetric === 'temp') {
      const colIdx = fieldIndexMap[`${locId}_temp`];
      if (colIdx !== undefined) {
        const vals = rows.map((r) => r[colIdx]).filter((v) => v !== null && v !== undefined);
        if (vals.length > 0) {
          const curr = vals[vals.length - 1];
          const min = Math.min(...vals);
          const max = Math.max(...vals);
          const avg = vals.reduce((a, b) => a + b, 0) / vals.length;

          html += `
            <tr>
              <td class="cell-loc" style="color: ${tempColor};">${locName}</td>
              <td class="cell-metric-temp" style="color: ${tempColor};">Temperatūra</td>
              <td><strong>${curr.toFixed(1)} °C</strong></td>
              <td>${min.toFixed(1)} °C</td>
              <td>${max.toFixed(1)} °C</td>
              <td>${avg.toFixed(1)} °C</td>
            </tr>
          `;
        }
      }
    }

    // Humidity Row
    if (state.activeMetric === 'all' || state.activeMetric === 'hum') {
      const colIdx = fieldIndexMap[`${locId}_hum`];
      if (colIdx !== undefined) {
        const vals = rows.map((r) => r[colIdx]).filter((v) => v !== null && v !== undefined);
        if (vals.length > 0) {
          const curr = vals[vals.length - 1];
          const min = Math.min(...vals);
          const max = Math.max(...vals);
          const avg = vals.reduce((a, b) => a + b, 0) / vals.length;

          html += `
            <tr>
              <td class="cell-loc" style="color: ${humColor};">${locName}</td>
              <td class="cell-metric-hum" style="color: ${humColor};">Mitrums</td>
              <td><strong>${Math.round(curr)} %</strong></td>
              <td>${Math.round(min)} %</td>
              <td>${Math.round(max)} %</td>
              <td>${Math.round(avg)} %</td>
            </tr>
          `;
        }
      }
    }
  });

  dom.analyticsTableBody.innerHTML = html || '<tr><td colspan="6" class="table-placeholder">Nav izvēlēta neviena vieta.</td></tr>';
}

function updateChartAndAnalytics() {
  const { rows, fields } = getFilteredSeriesData();
  initOrUpdateChart();
  updateAnalyticsTable(rows, fields);
}

// Event Listeners & UI Controls
function setupEventListeners() {
  dom.refreshBtn.addEventListener('click', async () => {
    dom.refreshIcon.classList.add('spinning');
    try {
      await loadLatestData();
      if (state.activeRange === 'month' && state.activeMonthId) {
        delete state.monthCache[state.activeMonthId];
        await selectMonth(state.activeMonthId);
      } else {
        await loadRecentHistory();
      }
    } finally {
      setTimeout(() => dom.refreshIcon.classList.remove('spinning'), 500);
    }
  });

  if (dom.monthSelect) {
    dom.monthSelect.addEventListener('change', async (e) => {
      const monthId = e.target.value;
      if (monthId) {
        await selectMonth(monthId);
      }
    });
  }

  dom.metricButtons.forEach((btn) => {
    btn.addEventListener('click', () => {
      dom.metricButtons.forEach((b) => b.classList.remove('active'));
      btn.classList.add('active');
      state.activeMetric = btn.dataset.metric;
      updateChartAndAnalytics();
    });
  });

  dom.locationChips.forEach((chip) => {
    chip.addEventListener('click', () => {
      const locId = chip.dataset.loc;
      if (state.activeLocations.has(locId)) {
        if (state.activeLocations.size > 1) {
          state.activeLocations.delete(locId);
          chip.classList.remove('active');
        }
      } else {
        state.activeLocations.add(locId);
        chip.classList.add('active');
      }
      updateChartAndAnalytics();
    });
  });

  dom.dismissAlertBtn.addEventListener('click', hideAlert);
}

function startAutoRefresh() {
  stopAutoRefresh();
  state.autoRefreshInterval = setInterval(async () => {
    if (state.autoRefresh) {
      await loadLatestData();
    }
  }, 60000);
}

function stopAutoRefresh() {
  if (state.autoRefreshInterval) {
    clearInterval(state.autoRefreshInterval);
    state.autoRefreshInterval = null;
  }
}

// Main Initialization
async function init() {
  setupEventListeners();

  state.relativeTimerInterval = setInterval(() => {
    if (state.lastSyncDate) {
      dom.lastUpdatedTime.textContent = `Atjaunināts: ${formatRelativeTime(state.lastSyncDate)}`;
    }
  }, 10000);

  await loadLatestData();
  await loadManifest();
  await loadRecentHistory();

  startAutoRefresh();
}

document.addEventListener('DOMContentLoaded', init);
