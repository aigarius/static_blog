<!--
.. title: Figuring out finances part 5
.. slug: figuring-out-finances-part-5
.. date: 2024-01-04 20:46:14 UTC
.. tags: Debian-planet,Ubuntu.lv-planet,blog,finances
.. category:
.. link:
.. description:
.. type: text
-->

At the end of the [last part](https://aigarius.com/blog/2023/10/29/finance-project-four/) of this,
we got a Home Assistant OS installation that contains in itself a Firefly III instance and that
contains all the current financial information. They are communicating and calculating predictions
for me.

The only part that I was not 100% happy with was accounting of cash transactions. You see payments
in cash are mostly made away from computer and sometimes even in areas without a mobile Internet
connection. And all Firefly III apps that I tried failed at the task of creating a new transaction
when offline. Even the one recommended Telegram bot from Firefly III page used a dialog-based
approach for creating even a simplest transaction. Issue asking for a one-shot transaction creation
option stands as unresolved.

Theoretically it would have been best if I could simply contribute that feature to that particular
Telegram bot ... but it's written in Javascript. By mapping the API onto tasks somehow. After about
4 hours I still could not figure out where in the code anything actually happens. It all looked like
just sugar or spagetty. Connectors on connectors on mappers.

So I did the real open-source thing and just wrote my own tool.
[firefly3_telegram_oneshot](https://github.com/aigarius/firefly3_telegram_oneshot) is a maximally simple
Telegram bot based on [python-telegram-bot](https://python-telegram-bot.org/) library.

So what does it do? The primary usage for me is to simply send a message to the bot at any time with
text like "23.2 coffee and cake" and when the message eventually reaches the bot, it then should
create a new transaction from my "cash" account to "Unknown" account in amount of 23.20€ and
description "coffee and cake".

That is the key. Everything else in the bot is comfort.

For example "/undo" command deletes the last transaction in cash account (presumably added by error)
and "/last" shows which transaction the "/undo" would delete.

And to help with expense categorisation one can also do a message like "6.1 beer, dest=Edeka, cat=alcohol"
that would search for a destination account that would fuzzy match to "Edeka" (a supermarket in Germany)
and add the transation to the category fuzzy matched to "alcohol", like "Shopping - alcoholic drinks".

And to make that fuzzy matching more reliable I also added "/cat something" and "/dest something" commands
that would show which category or destination account would be matched with a given string.

All of that in around 250 lines of Python code and executed by a 17 line Dockerfile (via the Portainer
on my Home Assistant OS). One remaining function that could be nice is creating a category or destination
account on request (for example when the first character of the supplied string is "+").

I am really plesantly surprised about how much can be done with how little code using the above Python
library. And you never need to have any open incoming ports anywhere to runs such bots, so the attack
surface for such bot-based service is much tighter.

All in all the system works and works well. The only exception is that for my particual bank there is
still no automatic way of extracting data about credit card transactions. For those I still have to manually
log into the Internet bank, export a CSV file and then feed that into the Firefly III importer. Annoying.
And I am not really motivated to try to hack my bank :D

Has this been useful to any of you? Any ideas to expand or improve what I have? Just find me as "aigarius" on
any social media and speak up :)
