<!--
.. title: Figuring out finances part 3
.. slug: finance-project-three
.. date: 2023-10-22 17:00:00 UTC
.. tags: Debian-planet,Ubuntu.lv-planet,blog,finances
.. category:
.. link:
.. description:
.. type: text
-->

So now that I have something that looks very much like a budgeting setup going, I am going to .. delete it! Why?
Well, at the end of the [last part](https://aigarius.com/blog/2023/10/15/finance-project-two/) of this,
the [Firefly III](https://www.firefly-iii.org/) instance was running on a tiny Debian server in a
Docker container right next to another Docker container that is running the main user of this server - a
[Home Assistant](https://www.home-assistant.io/) instance that has been managing my home for several
years already. So why change that?

See, there is one bit of knowledge that is very crucial to your Home Assistant experience, which is not really
emphasised enough in the Home Assistant documentation. In fact back when I was getting into the Home Assistant
both the main documentation and basically all the guides around were just coming off the hype of Docker disrupting
everything and that is a big reason why everyone suggested to install and use
[Home Assistant as a Docker](https://www.home-assistant.io/installation/generic-x86-64#install-home-assistant-container)
container on top of any kind of stable OS. In fact I used to run it for years on my [TerraMaster NAS](https://www.terra-master.com/uk/f2-221.html), just so
that I don't have a separate home server running 24/7 at home and just have everything inside the very compact
NAS case.

So here is the thing you ***NEED*** to know - Home Assistant Container is ***DEMO*** version of Home Assistant!
If you want to have a full Home Assistant experience and use the knowledge of the huge community around the HA
space, you ***have to*** use the [Home Assistant OS](https://www.home-assistant.io/installation/generic-x86-64#install-home-assistant-operating-system). Ideally on dedicated hardware. Ideally on [HA Green](https://www.home-assistant.io/green) box, but
any [tiny PC](https://www.csl-computer.com/en/pc-systems/mini-pcs/csl-narrow-box-compact-v5/mini-pc-csl-narrow-box-ultra-hd-compact-v5-windows-11-home.html)
would also work great. [Raspberry Pi 4+](https://www.raspberrypi.com/products/raspberry-pi-5/) is common, but quite weak as the network
size grows and especially the SD card for storage gets old *very* fast. Get a real small x86 PC with at least
4Gb RAM and a NVME SSD (eMMC is fine too). You want to have an Ethernet port and a few free USB ports. I would
also suggest immediately getting [HA SkyConnect adapter](https://www.home-assistant.io/skyconnect) that can do Zigbee networking and will do Matter soon
(tm). I am making do with a [SonOff Zigbee](https://itead.cc/product/sonoff-zbbridge/) gateway,
but it is [quite hacky](https://digiblur.com/2020/07/25/how-to-use-the-sonoff-zigbee-bridge-with-home-assistant-tasmota/) to get working and your whole
Zigbee communication breaks down if the WiFi goes down - suboptimal.

So I took a backup of the Home Assistant instance using it's build-in tools. I took an export of my fully
configured Firefly III instance and proceeded to wipe the drive of the NUC. That was not a smart idea. :D

On the Home Assitant side I was really frustrated by [the documentation](https://www.home-assistant.io/installation/generic-x86-64#write-the-image-to-your-boot-medium) that
was really focused on users that are (likely) using Windows and are using an SD card in
something like Raspberry Pi to get Home Assistant OS running.
It recommended downloading [Etcher](https://www.balena.io/etcher) to write the image to the boot medium. That is a really weird piece of
software that managed to actually crash consistently when I was trying to run it from Debian Live or Ubuntu
Live on my NUC. It took me way too long to give up and try something much simpler - dd.

```xzcat haos_generic-x86-64-11.0.img.xz | dd of=/dev/mmcblk0 bs=1M```

That just worked, prefectly and really fast. If you want to use a GUI in a live environment, then just using
the gnome-disk-utility ("Disks" in Gnome menu) and using the "Restore Disk Image ..." on a partition would
work just as well. It even supports decompressing the XZ images directly while writing.

But that image is small, will it not have a ton of unused disk space behind the fixed install partition? Yes,
it will ... until first boot. The HA OS takes over the empty space after its install partition on the first
boot-up and just grows its main partition to take up all the remaining space. Smart. After first boot is
completed, the first boot wizard can be accessed via your web browser and one of the prominent buttons there
is restoring from backup. So you just give it the backup file and wait. Sadly the restore does not actually give
any kind of progress, so your only way to figure out when it is done is opening the same web adress in another
browser tab and refresh periodically - after restoring from backup it just boots into the same config at it had
before - all the settings, all the devices, all the history is preserved. Even authentification tokens are
preserved so if yu had a [Home Assitant Mobile](https://companion.home-assistant.io/) installed on your phone (both for remote access and to send
location info and phone state, like charging, to HA to trigger automations) then it will just suddenly start
working again without further actions needed from your side. That is an almost perfect backup/restore experience.

The first thing you get for using the OS version of HA is easy automatic update that also automatically takes
a backup before upgrade, so if anything breaks you can roll back with one click. There is also a command-line
tool that allows to upgrade, but also [downgrade ha-core](https://community.home-assistant.io/t/downgrading/414612/2) and other modules. I had to use it today as HA version
23.10.4 actually broke support for the Sonoff bridge that I am using to control Zigbee devices, which are like
90% of all smart devices in my home. Really helpful stuff, but not a must have.

What *is* a must have and that you can (really) only get with Home Assistant Operating System are [Addons](https://www.home-assistant.io/addons/). Some
addons are just normal servers you can run alongside HA on the same HA OS server, like MariaDB or Plex or a
file server. That is not the most important bit, but even there the software comes pre-configured to use in
a home server configuration and has a very simple config UI to pre-configure key settings, like users,
passwords and database accesses for MariaDB - you can litereally in a few clicks and few strings make serveral
users each with its own access to its own database. Couple more clicks and the DB is running and will be kept
restarted in case of failures.

But the *real* gems in the Home Assistant Addon Store are modules that extend Home Assitant core functionality
in way that would be *really* hard or near impossible to configure in Home Assitant Container manually,
especially because no documentation has ever existed for such manual config - everyone just tells you to
install the addon from HA Addon store or from HACS. Or you can read the addon metadata in various repos and
figure out what containers it actually runs with what settings and configs and what hooks it puts into the HA
Core to make them cooperate. And then do it all over again when a new version breaks everything 6 months later
when you have already forgotten everything. In the Addons that show up immediately after installation are
addons to install the new [Matter](https://www.home-assistant.io/blog/2023/02/08/state-of-matter-and-thread/)
server, a MariaDB and [MQTT](https://www.home-assistant.io/integrations/mqtt/) server
(that other addons can use for data storage
and message exchange), Z-Wave support and ESPHome integration and very handy File manager that includes
editors to edit Home Assitant configs directly in brower and SSH/Terminal addon that boht allows SSH
connection and also a
web based terminal that gives access to the OS itself and also to a comand line interface, for example, to
do package downgrades if needed or see detailed logs. And also there is where you can get the features
that are the focus this year for HA developers - [voice enablers](https://www.home-assistant.io/blog/2023/10/12/year-of-the-voice-chapter-4-wakewords/).

However that is only a beginning. Like in Debian you can add additional repositories to expand your list of
available addons. Unlike Debian [most of the amazing software](https://community.home-assistant.io/tag/hassio-repository) that is available for Home Assistant is outside
the main, official addon store. For now I have added the most popular addon repository - [HACS](https://hacs.xyz/) (Home Assistant
Community Store) and repository maintained by [Alexbelgium](https://github.com/alexbelgium/hassio-addons). The first includes things like NodeRED (a workflow
based automation programming UI), Tailscale/Wirescale for VPN servers, motionEye for CCTV control, Plex for
home streaming. HACS also includes a *lot* of HA UI enhacement modules, like themes, custom UI control panels
like Mushroom or mini-graph-card and integrations that provide more advanced functions, but also require
more knowledge to use, like Local Tuya - that is harder to set up, but allows fully local control of (normally)
cloud-based devices. And it has [AppDaemon](https://appdaemon.readthedocs.io/) - basically a Python based automation framework where you put in
Python scrips that get run in a special environment where they get fed events from Home Assistant and can
trigger back events that can control everything HA can and also do anything Python can do. This I will need
to explore later.

And the repository by Alex includes the thing that is actually *the* focus of this blog post (I know :D) -
Firefly III addon and Firefly Importer addon that you can then add to your Home Assistant OS with a few
clicks. It also has all kinds of addons for NAS management, photo/video server, book servers and
[Portainer](https://community.home-assistant.io/t/home-assistant-community-add-on-portainer/68836) that
lets us setup and run *any* Docker container inside the HA OS structure. HA OS *will* detect this and warn you
about unsupported processes running on your HA OS instance (nice security feature!), but you can just dismiss
that. This will be very helpful very soon.

This whole environment of OS and containers and apps really made me think - what was missing in Debian that
made the talented developers behind all of that to spend the immense time and effor to setup a completely
new OS and app infrastructure and develop a completel paraller developer community for Home Assistant apps,
interfaces and configurations. Is there *anything* that can still be done to make HA community and the
general open source and Debian community closer together? HA devs are not doing anything *wrong*: they are
using the best open source can provide, they bring it to people whould could not install and use it otherwise,
they are contributing fixes and improvements as well. But there must be some way to do this better, together.

So I installed MariaDB, create a user and database for Firefly. I installed Firefly III and configured
it to use the MariaDB with the web config UI. When I went into the Firefly III web UI I was confronted with
the normal wizard to setup a new instance. And no reference to any backup restore. Hmm, ok. Maybe that goes
via the Importer? So I make an access token again, configured the Importer to use that, configured the
Nordlinger bank connection settings. Then I tried to import the export that I downloaded from Firefly III
before. The importer did not auto-recognose the format. Turns out it is just a list of transactions ...
It can only be barely useful if you first manually create all the asset accounts with the same names as
before and even then you'll again have to deal with resolving the problem of transfers showing up twice.
And all of your categories (that have not been used yet) are gone, your automation rules and bills are gone,
your budgets and piggy banks are gone. Boooo. It will be easier for me to recreate my account data from
bank exports again than to resolve data in that transaction export.

Turns out that Firefly III documenation [explicitly](https://docs.firefly-iii.org/firefly-iii/advanced-installation/backup/)
recommends making a mysqldump of your own and not rely
on anything in the app itself for backup purposes. Kind of sad this was not mentioned in the export page
that sure looked a lot like a backup :D

After doing all that work all over again I needed to make *something* new not to feel like I wasted days of
work for no real gain. So I started solving a problem I had for a while already - how do I add cash
transations to the system when I am out of the house with just my phone in the hand? So far my workaround has
been just sending myself messages in WhatsApp with the amount and description of any cash expenses. Two
solutions are possible: app and bot.

There are actually *multiple* [Android-based phone apps that work with Firefly III API](https://docs.firefly-iii.org/firefly-iii/more-information/3rdparty/#mobile-applications) to do full
financial management from the phone. However, after trying it out, that is not what I will be using most
of the time. First of all this requires your Firefly III instance to be accessible from the Internet. Either
via direct API access using some port forwarding and secured with HTTPS and good access tokens, or via
a VPN server redirect that is installed on both HA and your phone. Tailscale was really easy to get working.
But the power has its drawbacks - adding a new cash transaction requires opening the app, choosing new
transaction view, entering descriptio, amount, choosing "Cash" as source account and optionally choosing
destination expense account, choosing category and budget and then submitting the form to the server.
Sadly none of that really works if you have no Internet or bad Internet at the place where you are using
cash. And it's just too many steps. Annoying.

An easier alternative is setting up a [Telegram bot](https://github.com/cyxou/firefly-iii-telegram-bot) -
it is running in a custom Docker container right
next to your Firefly (via Portainer) and you talk to it via a [custom Telegram chat channel](https://core.telegram.org/bots/tutorial#obtain-your-bot-token) that you create
very easily and quickly. And then you can just tell it "Coffee 5" and it will create a transaction
from the (default) cash account in 5€ amount with description "Coffee". This part also works if you are
offline at the moment - the bot will receive the message once you get back online. You can use Telegram
bot menu system to edit the transaction to add categories or expense accounts, but this part only work
if you are online. And the Firefly instance does not have to be online at all. Really nifty.

So next week I will need to write up all the regular payments as bills in Firefly (again) and then I can start
writing a Python script to predict my (financial) future!
