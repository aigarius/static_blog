<!--
.. title: Half a year with iX3
.. slug: half-a-year-with-iX3
.. date: 2026-08-30 10:00:00 UTC
.. tags: Debian-planet,Ubuntu.lv-planet,blog,hardware,car,work
.. category:
.. link:
.. description:
.. type: text
-->

# Jumping a generation of electric cars

This February (2026) marks a full 10 years since I started working for BMW, and
a key employment bonus is the ability to drive a company car on special two-year
leasing terms. Just before the new year 2026 started, I said [goodbye to my
latest company car](https://aigarius.com/blog/2026/01/07/sedan-experience/).

Now this spring I was able to pick a new car, a car that I have been waiting for
and working on for the past ~5 years - the BMW iX3 Neue Klasse. It is a *very*
special car for BMW and also for electromobility in general.

<!-- TEASER_END -->

## Neue Klasse

So what is this Neue Klasse thing and why am I so excited about. The phrase
just means "the new class". It is a reference to BMW Neue Klasse cars from
all the way back in 1962 starting with BMW 1500. The BMW was in a very bad
financial situation after the WW2 and did not really recover in the 1950s
either. BMW had either luxury cars or motorcycles (and tiny cars powered by
motorcycle engines, like the Isetta, that pulled BMW trough the 1950s in the
financial sense). With the German (and European) population recoving from the
war and demanding more powerful cars, BMW needed a completely new development
in this segment.

So they did. BMW invested *heavily* to develop a completely new car *and* also
a completely new engine to go into that car, which BMW had not done since 1933.
BMW 1500 was introduced in 1962. In 1963 sales increased by 47% year over year
and the company had the first profitable year after a long gap. Before 1970,
three more model lines - 1800, 1600 and 2000 were introduced, all on the same
architecture, with a bunch of derivive models.

What we know now as modern BMW car line-up and model offering was born in the
1962 Neue Klasse product launch.

A lot of the above is also true for this, 2026 Neue Klasse product launch. It
is a massive investemnt, massive engineering project that ran over many years.
Every part and system in the Neue Klasse is new. Build from ground up. Designed
from scratch with the experience of over a century of car design. Designed as
electric-first architecture (range-extenders are possible) with all parts of
the system being architected together on a high level with freedom to move,
split or consolidate functionality across the whole car.

In the end it has completely new batteries with ground-breaking cells and
unprecedented battery management system that allows fitting normal 3 series
cars with over 110 kWh of battery and allow those batteries to reliably charge
at 400 kW without long term damage and also give that power back in massive
bursts without overheating. Completely new electric motors with build-in
reductors and differentials in a sealed maintenance-free system that is
also ~30% more efficient than previous generation.

The motor controllers and brake controllers and regen controllers and body
dynamics controllers were all rolled into one system dubbed Heart of Joy which
is essentially a real-time supercomputer. It is a true real-time system that
is guaranteed to process inputs at 1000 Hz rate (full input, to output
roundtrip, with real-time guarantees), which is about 10 times faster than
best previous systems. You can really feel the difference. The car just
drives, it does not slip or skid or jerk.

The "party trick" of Heart of Joy is to simply remove the foot from the
accelerator, ask the passengers to close their eyes and ask them to tell
when exactly has the car come to a full stop. We all know the "stop jerk"
that all cars have in the last moment. BMW Neue Klasse does not have that.
The transition from rolling to regenerating to stopped is so smooth that
you don't even feel it. That is not the reason it was built, it's a
side-effect - this is what you get when you perfect the control over
motor power, regen, traction, brakes and stability controls.

The iX3 NK also gained far more space internally than previous iX3, including
gaining a frunk. And the aerodynamics are much smoother, gaining efficiency.

## Software

The BMW Neue Klasse is built on the IDCEvo platform, which is no longer related
to the previous MGU system that I described in
my [Debconf talk back in Montreal](https://debconf17.debconf.org/talks/33/).

It is still based on a custom Linux build compiled with Yocto with GENIVI
protocols like DLT and SomeIP connecting all the components. However, the
UI part of this system is now being build on top of Android AOSP stack and
no longer a custom binary running on Wayland.

It is quite a radical concept. BMW first tried it on IDC23 platform that was
integated into the Mini models for the past few years. The benefits were very
much worth the extra effort in adapting to Googles requirements. For example,
it becomes much easier to take an existing Android app and adapt it to work
perfectly in a car context. I have a
lot of thoughts on this development and its wider implications. I *hope* to
be able to attend Debconf 27 in Japan and give a talk there about this
subject in a bit more depth.

In addition to the "normal" central infotainment screen, all Neue Klasse
cars also will come with "Panoramic Vision" display that "spans" the gap
between the instrument panel of the car and the actual windscreen. In
reality it is composed from 3 separate screens. The left one is in front of
the driver and has all the normal instrument cluster info (speed, gear,
status of assist systems, range). The middle and right screen are customizable.
They can have an arrangement of pre-defined widgets - 3 per screen (like I
love to have a widge that *always* shows altitude above sea level) or wider
widgets specific to driving mode, like Sport mode gets a two-axis g-force
meter with heatmap as one of the options.

This part is what I have been working on (or more correctly, making an
environemnt for a bunch of other teams to work on) for the past 5-6 years.

## Charging

Basically, everything that I said about the i4
[before](https://aigarius.com/blog/2022/06/29/long-travel-in-an-electric-car/)
also applies to the iX3 NK, but with a *big* twist. The Neue Klass cars feel
like they are *basically* __twice__ as good as the previous generation. Each
system and parameter is improved by significant margins, like +20% here and
+30%, but all those effects add up and create something that feel *far*
more powerful than the sum of those parts.

In the end, I don't even talk about charging speeds or consumption anymore.
Instead, in real life, I think about charging and consumption in terms of time,
and then it sounds like this:

- In Germany (speeds around 180 km/h): from full charge, drive ~4 hours, charge
  for 20 minutes, drive another ~3 hours
- On highways outside Germany (~140 km/h): from full charge, drive ~6 hours,
  charge for 20 minutes, drive another ~4 hours
- On regional roads (90–100 km/h): from full charge, drive ~9 hours, charge for
  15 minutes, and drive another ~6 hours

Compare that to what [I wrote](https://aigarius.com/blog/2026/01/07/sedan-experience/)
about i5 from just last year. It does not look *all* that different in numbers,
but what happens when you project that to a context of a day?

I did two massive road trips in the new iX3 over the past couple of months. One
drive from Germany to Latvia (2000 km each way + 2000 km driving around Latvia)
and one drive from Germany to Badaran, Spain to see the solar eclipse (1600 km
each way with about 500 km detour on the way back). The average consumption
towards Latvia was around 18.4 kWh/100km and to Spain was 19.1 kWh/100km. France
highways are much faster (140 km/h) than local roads in Latvia (90 km/h).
While we were driving around Latvia the typical consumption was around
15 kWh/100km or even below that when it was not too hot outside.

So, how do the hours I mentioned above translate to real driving?

- 9+ hours of driving on 90-100 km/h roads means that, if I leave in the
   morning with a full battery, I will not need to charge that day at all.
   Real driving involves sometimes also stopping to do something, driving
   even slower in cities, traffic, repair works, ... all of which only
   extend the driving range. In the end you'd need to work *really* hard
   to drain the iX3 battery in one real day before going to sleep, if the
   max speed in that area is 90/100 km/h.
- 6 hours + 4 hours in countries with ~140 km/h speed limit means that
   basically everywhere (outside Germany) all you need to do to drive a
   full day with the iX3 is to find *one* opportunity to coincidentally
   stop near a fast charger in the later part of the afternoon for some
   20 minutes, for example while grabbing a fast bite to eat or visiting
   a bathroom. That is it. The rest of the day you can be flying down
   the highway. We did this in Poland and France.
- Germany is special, but even here you could basically cross the whole
   country in two stops while travelling at top speed the whole time.

A colegue of mine drove my car, with 4 passengers and some luggage, at maximal
speed (213-215 km/h) all the way from Ulm to Munich and back (where speed limits
allowed so) and despite all that he still came back with 15% of battery remaining.
Few people can maintain the high level of focus and stress that such speeds
demand for long enough to fully drain the iX3 battery.

And what if you want to drive at max speed a bit longer and you are still
20-30% short? Well, just stop at a 400kW charger (or 300kW+) at ~10 SOC 
for 5 minutes and you will get your missing range. The recharge speed is
trully mind-bending.

During our long distance road trips we (experienced road-trippers!) already
had to concede defeat a handful of times and stop for a bathroom break or
coffee *before* the cars battery was empty. This car has more endurance than
we do. It broke the barrier. We no longer wait on the car - it waits on us.

And the most destructive moment? We are driving the whole day already, the
car wants to drive another hour before recharging, but we can not. We pick the
next rest stop with a bathroom and a fast charger. We stop, plug in, go to
the bathroom and come right back and drive off. And you know what this
car tells us? It plans the next charging stop now 2 and a half hours away!
And now we are starving :D

## What's next?

I will have this car until spring of 2028. Then I will be able to choose
what I want to drive next.

The iX3 is not the only Neue Klasse car. In fact
*ALL* BMW cars will become Neue Klasse cars over this next model refresh
cycle. The new i3 was already shown. And the iX5 as well. It is not a
secret that updated iX4 and i5 are coming. As well as i3 Touring and a
full-blodied electric M series car, presumably with 4 motors. Extension
of the range down to i1/iX1 and up to i7/iX7 is not hard to imagine.

BMW customers *love* the new iX3 and are buying it (and the new i3) in
massive numbers. So there is zero doubt that this wave of transformation
is going forward.

With that in mind I *hope* to be able to pick up a Neue Klasse version
of i5 again. The seats there were a *godsend* for my ageing back. But
it might be that for cost and practicality reasons I'd rather need to
go for the i3 Touring.

It is trully a completely new place where we can look forward to
choosing between multiple very viable BEV models at the same time. I
do expect that vast majority of BMW sales in Europe will be BEVs before
2030, never mind 2035.

Questions? Feedback? Just ask
[here](https://bsky.app/profile/aigarius.com/post/3mud33aggps27) or
[here](https://www.threads.com/share/E0vb1HczO/).
