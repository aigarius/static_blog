<!--
.. title: Figuring out finances part 1
.. slug: finance-project-start
.. date: 2023-10-09 17:00:00 UTC
.. tags: Debian-planet,Ubuntu.lv-planet,blog,finances
.. category:
.. link:
.. description:
.. type: text
-->

I have been managing my finances and getting an overview of where I am financially and where I am
going month-to-month for a few years already. That means that I already have *a* method of doing
my finances and a method of thinking about them. So far this has been supported by a commerical
tool called MoneyWiz. I was happy to pay them for the ability to have a solid product and be able
to easily access my finances from my phone (to enter cash transactions directly in the field) and
sync data across multiple devices with their cloud offering. However, MoneyWiz development stalled.
So much so that they stopped updating their Android app and cancelled web version plans to just focus
on a iPhone and MacOS clients. And even there the development did not seem very successful over the
last year. So I am cancelling their subscription, extracting all my data (as CSV) and looking for
alternatives.

So let's start with the basics - what I want from finace software?

* Open source and self-hosted
* Accounts to represent real accounts in my bank, credit cards, cash account
* Transactions to represent money moving in/out/between accounts
* Tree of categories for transactions to categorise spending
* Category reports on arbitrary time periods
* Ability to see the expected balance on each account at any historic point in time from given transactions
* Ability to do a corrective transaction - hmm, I don't know what happened, but right now I have X€ in cash
* Adding past transactions before a corrective transaction should not change balance *after* correction
* Ability to automatically import transactions from my bank
* Ability to plan future, recurring transactions
* Incoming transactions from bank import should be auto-matched with planned recuring transactions
* Ability to see missed planned recurring transactions
* Ability to see value deviations in planned recuring transactions
* Ability to manually match a transaction with a planned recurring transaction for that month or skip a month
* Ability to see a *projected* balance on my accounts at any future date given planned transactions
* Credit card fully refilling its current (negative) balance to zero (from a given account) should be a plannable transaction
* Accessible from multiple devices, like Linux, Android, iPhone, MacOS. Most likely that means web-based
* Achiving accounts without loosing their past transactions with active accounts
* API to access data, so that I could wire that up to a Home Assistant dashboard

I don't care about currencies (thanks Euro!), localization, taxes and double-entry bookkeeping. I don't have much use for tags,
budgets or savings targets.

It could be useful to be able to track stock investment values (but I do have a pretty good from the bank that does that anyway).
And tracking loans (incoming and outgoing) could be a worthwhile thing as well, but that can also be simulated with separate
accounts for each loan. Tracking refundable expenses (like medical expenses that insurances should refund later on) would also be
nice. Could also be simulated by having a separate expense category (Medical - refundable) and putting the refund as a negative
expense into that category.

One weird feature that I really like is having transfer transactions that have arbitrary incoming and outgoing dates. For some
transactions it is a simple transfer delay - money leaves the account A on Friday and only appears in the destination account B
on Monday morning. However, this can also happen the other way around - a few credit cards I have seen work in a way that on
14th of each month the balance of the credit card gets reset to zero and then a week later the negative balance that was on that
credit card gets taken from the base account that the card is bound to. So the money leaves the base account a week *later* than
it arrives in the credit card account. Financial systems really are magic sometimes :D

Ideally that should be represented by a single transaction with two dates - one date when money leaves one account and another date
when it arrives in a different account, so that balances on both accounts in the days between would be correct (as in matching what
the bank says they were on those dates). *And* it should automatch such transaction from bank data imports. And predict its value
from the negative balance of the credit card. And a pony! But in worst case this could be simulated using a separate "In transfer"
account.

When I am thinking about my finances, the *key* metric for me is - how much will I spend this month - both in fixed spending (rent,
Internet and phone bills, health insurance, subscriptions, ...) and in variable spending (groceries, eating out, clothing, ...). In
theory that *should* be trivial, but in practice a simple calendar month view will fail because a bunch of fixed expenses occur
at the month end/start boundary and can happen *either* at the end of previous month or at start on next month, depending on how
the weekends happen to fall and how the systems of various providers decided to do direct debits this month. So 1st of month is not
a good snapshoting time. Any date between 6th (last possible days for monthly bills) and 20th (earliest possible salary day) would
be a better cut off point. Looking at the balance of my main account at that time point lets me know what was the difference between
income and expenses for the past month. And that is the number I want the financial app to be able to predict as soon as possible.

And additional complication is the way credit cards work here. The expenses booked to a credit card after 14th of September will only
appear in the main account on 20th of October and thus will actually only count towards the expenses of month of October. That makes
it very confusing to see a larger overspend in the main account on 6th of October and then use the categories to try to figure out
where the money went, because all the spending that happened on the credit card after the 14th of September should not really be
looked at in that context, but spending on the main account or cash account *should* be counted all the way to 6th of October. :D

I am not optimistic that *any* finance software would able to doea with this mess correctly.

So far I am tending to consider [Firefly III](https://docs.firefly-iii.org/firefly-iii/) which has *most* of what I need and looks
great and well maintained, but has the tiny drawback of being written in PHP, so that basically excludes me from ability to
contribute anything beyond ideas and feedback. :D

I already did a quick test of Firefly via local Docker containers, so the next step would be to try to set it up as a production
instance (using the same always-on mini PC that is running my Home Assistant instance), get the database up and working, get the
Firefly III itself up and running, get account importer working for bank connection, import historical transactions from there,
setup my categories and recurring transactions, import past data dumped out of MoneyWiz and see if this works well and gives
me the insights I need.

If you know a better solution, please let me know on any social or email channel!
