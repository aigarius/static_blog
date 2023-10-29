<!--
.. title: Figuring out finances part 4
.. slug: finance-project-four
.. date: 2023-10-29 17:00:00 UTC
.. tags: Debian-planet,Ubuntu.lv-planet,blog,finances
.. category:
.. link:
.. description:
.. type: text
-->

At the end of the [last part](https://aigarius.com/blog/2023/10/22/finance-project-three/) of this,
we got a Home Assistant OS installation that contains in itself a Firefly III instance and that
contains all the current financial information. Now I will try to connect the two.

While it could be nice to create a fully-featured integration for Firefly III to Home Assistant
to communicate all interesting values and events, I have an interest on programming a more
advanced data point calculation for my budget needs, so a less generic, but more flexible approch
is a better one for me. So I was quite interested when among the addons in the Home Assistant
Addon Store I saw [AppDaemon](https://appdaemon.readthedocs.io/en/latest/index.html) - a way
to simply integrate arbitrary Python processing with Home Assistant. Let's see if that can do
what I want.

For start, after reading [the tutorial](https://appdaemon.readthedocs.io/en/latest/HASS_TUTORIAL.html)
, I wanted to create a simple script that would use
[Firefly III REST API](https://docs.firefly-iii.org/firefly-iii/api/) to read the current
balance of my main account and then send that to Home Assistant as a sensor value, which then
can be displayed on a dashboard.

As a quick try I modified the provided hello_world.py that is included in the default
AppDaemon installation:

``` python
import requests
from datetime import datetime
import appdaemon.plugins.hass.hassapi as hass
app_token = "<FIREFLY_PERSONAL_ACCESS_TOKEN>"
firefly_url = "<FIREFLY_URL>"

class HelloWorld(hass.Hass):
    def initialize(self):
        self.run_every(self.set_asset, "now", 60 * 60)

    def set_asset(self, kwargs):
        ent = self.get_entity("sensor.firefly3_asset_sparkasse_main")
        if not ent.exists():
            ent.add(
                state=0.0,
                attributes={
                    "native_value": 0.0,
                    "native_unit_of_measurement": "EUR",
                    "state_class": "measurement",
                    "device_class": "monetary",
                    "current_balance_date": datetime.now(),
                })

        r = requests.get(
            firefly_url + "/api/v1/accounts?type=asset",
            headers={
                "Authorization": "Bearer " + app_token,
                "Accept": "application/vnd.api+json",
                "Content-Type": "application/json",
        })
        data = r.json()
        for account in data["data"]:
            if not "attributes" in account or "name" not in account["attributes"]:
                continue
            if account["attributes"]["name"] != "Sparkasse giro":
                continue
            self.log("Account :" + str(account["attributes"]))
            ent.set_state(
                state=account["attributes"]["current_balance"],
                attributes={
                    "native_value": account["attributes"]["current_balance"],
                    "current_balance_date": datetime.fromisoformat(account["attributes"]["current_balance_date"]),
                })
            self.log("Entity updated")
```

It uses a URL and personal access token to access Firefly III API, gets the asset accounts information,
then extracts info about current balance and balance date of my main account and then creates and/or
updates a "sensor" value into Home Assistant. This sensor is with
[metadata](https://developers.home-assistant.io/docs/core/entity/sensor/)
marked as a monetary value and as a measurement. This makes Home Assistant track this value in the
database as a graphable changing value.

I modified the file using the File Editor addon to edit the `/config/appdaemon/apps/hello.py` file. Each
time the file is saved it is reloaded and logs can be seen in the AppDaemon Logs section - main_log for
logging messages or error_log if there is a crash. Useful to know that
[requests](https://requests.readthedocs.io/en/latest/) library is included, but it hard to see in the
docks what else is included or if there is an easy way to install extra Python packages.

This is already a very nice basis for custom value insertion into Home Assistant - whatever you can with
a Python script extract or calculate, you can also inject into Home Assistant.
With even this simple approach you can monitor balances, budgets, piggy-banks, bill payment status and
even sum of transactions in particular catories in a particular time window. Especially interesting data
can be found in the insight section of the Firefly III API.

The script above uses a trigger
like `self.run_every(self.set_asset, "now", 60 * 60)` to simply run once per hour. The data in Firefly will not
be updated too often anyway, at least not until we figure out how to make bank connection run automatically
without user interaction and not screw up already existing transactions along the way. In theory a
[webhook API](https://docs.firefly-iii.org/firefly-iii/features/webhooks/) of the Firefly III
could be used to trigger the data update instantly when any transaction is created or updated. Possibly
even using Home Assistant
[webhook integration](https://www.home-assistant.io/docs/automation/trigger/#webhook-trigger). Hmmm. Maybe.

Who am I kiddind? I am *going* to make that work, for sure! :D But first - how about figuring out the future?

So what I want to do? In short, I want to predict what will be the balance on my main account just
*before* the next months salary comes in. To do this I would:

* take the current balance of the main account
* if this months salary is not paid out yet, then add that into the balance
* deduct all still unpaid bills that are due between now and the target date
* if the credit card account has not yet been reset to the main account, deduct current amount on the cards
* if credit card account has been reset, but not from main account deducted yet, deduct the reset amount

To do that I need to use the Firefly API to read: current account info, status of all bills including
next due date and amount, transfer transactions between credit cards and main account and something
that would store the expected salary date and amount. Ideally I'd use a recurring transaction or a income
bill for this, but Firefly is not really cooperating with that. The easiest would be just to hardcode that
in the script itself.

And [this](https://github.com/aigarius/firefly3_ha_oracle) is what I have come up with so far.

To make the development process easier, I separated put the params for the
API key and salary info and app params for the month to predict for, and predict both this and next
months balances at the same time. I edited
the script locally with Neovim and also ran it locally with a few mocks, uploading to Home Assistant
via the SSH addon when the local executions looked good.

So what's next? Well, need to somewhat automate the sync with the bank (if at all possible). And for sure
take a regular database and config backup :D
