<!--
.. title: Optimistic take on AI
.. slug: optimistic-take-on-ai
.. date: 2026-08-22 19:30:00 UTC
.. tags: Debian-planet,Ubuntu.lv-planet,blog,photo
.. category:
.. link:
.. description:
.. type: text
-->

As I am writing this, there is a [vote](https://www.debian.org/vote/2026/vote_002) ongoing in the Debian
project on how to deal with AI in general and AI-assisted contributions to Debian specifically. Massive discussions
have happened in [debian-vote](https://lists.debian.org/debian-vote/) and other locations. I have also asked
questions there and offered my perspective. IMHO now is the time to summarize that, after all the discussions
that I've had with people on multiple sides of this debate both online and offline, and explain how I will be
voting and why. Hopefully that will be helpful to someone else as well. None of this has been compiled with AI
assistance, but only because I think that forming opinions is not something where AI can really be helpful.
Spellcheck was used though.

So, first I will describe how I see each of the 8 proposals, then what my vote will be, and then a bit more
detail on the reasoning and thinking behind this. WARNING - this went *long*.

* Proposal A - Action: ban all AI-assisted contributions via Social Contract amendment, except from upstreams
 (so not rolling back the Linux kernel and other software to "pure", pre-AI state). Claims that copyright/licensing
 status is unclear, quality is bad, community is being destroyed, web resources see extra load and that training
 consumes "staggering" resources. Needs 2/3rd majority to pass. - IMHO worst and most inconsistent. If copyright
 and licensing of AI products *is* unclear, then be consistent - ban ALL software with AI contributions, fork Linux
 kernel and other software from pre-AI versions, reject all security fixes of issues found with AI. Quality section
 lists problems that have not existed in the real world since at least a year of rapid AI coding development. Community
 section assumes that now all Debian contributions will be drive-by AI slop and no one will learn anything anymore.
 Ethics section mixes up effects of badly configured systems (AI web load is no different from load from a badly
 configured Perl script) with claimed "resource" usage without any context, taking on trust project ambitions of
 startups and assuming exponential growth. And then concludes that delivering less is in the interest of our
 users somehow.

* Proposal B - Action: allow AI-assisted contributions, with conditions of: legality, accountability, disclosure,
  no uncoordinated bulk actions, privacy. Concerns on quality and legal status as well as environmental impact
  and scraper load are noted, but not really addressed beyond labelling them as concerns. - IMHO it is an ok starting
  position as it establishes that each contributing *person* must still be fully responsible for *their*
  contribution (both legally and technically) and for that has to also understand (and review) what they submit.
  Disclosure lets others know to watch out for other classes of problems when code was changed with AI assistance.
  Prior discussion for bulk changes just says that the (already established) practice should not be neglected
  just because now large changes are easier to do. And the privacy part warns against accidentally sending private or
  confidential data (like a not yet published security bug) to a public service where it could become public.
  Personally I would have liked a stronger statement to encourage use of environmentally responsible AI services
  and local AI tools. Possibly a preference for open-weight models with a clear path forward to preferring truly
  free AI models, when such a category of products could be clearly delineated and established.

* Proposal C - Action: reject AI-assisted contributions at Code of Conduct level. Claims all the world's evils come
  from LLMs and that "Ethical and safe use of this technology is almost impossible". Goes as far as banning any
  use of LLMs even in Debian mailing list emails and Debian Planet blog posts - if you do, it's a CoC violation
  and may result in exclusion from the project. Additionally *mandates* the disclosure of the usage ... presumably
  to ban you more efficiently for it. - IMHO truly a dictatorial nightmare option. Zero actual reasoning or
  basis for such a decision. Zero sources. Nothing claimed in this option's rationale is even close to reality and
  nothing claimed there is in any way related to the actual technology being discussed. Like, an "LLM" does not
  automagically commit "fraud" when you use it, like this proposal claims, as if that was a well-known fact.
  LLMs are not all "owned by horrible people and companies". Even if some include a (prominent Debian user,
  long-time supporter and sponsor) Google into "horrible companies" (which is what this proposal implies!),
  there are plenty of LLMs owned by all kinds of companies all over the world and there are plenty of open-weight
  LLMs that are not really owned by anyone. Most invasive and dishonest option on the ballot.

* Proposal D - Action: allow AI-assisted contributions, with conditions of: legality, accountability,
  disclosure, privacy. IMHO same as B, just shorter. Adds a "we don't recommend" towards others developing software
  with AI assistance. Seems pretty weird to add that and then immediately accept Debian contributors doing so.
  Assumes that the bulk change bit of B is implied as AI is just tooling, so bulk changes should be pre-discussed
  just like today - so no change and thus no point in mentioning that. Fair. D is a bit more explicit on expected
  technical details - like that the "person" submitting the change is supposed to sign it, not AI. Notable is
  the complete absence of resource usage or the environment from concerns. IMHO it would be better to have that
  and also recommendations on how to avoid causing environmental damage when using AI.

* Proposal E - Action: no action as such - AI-assisted contributions must follow the same rules as all other
  contributions and those rules are sufficient. IMHO despite its length this is a very well-worded position
  statement that describes how and why AI-assisted contributions already work perfectly fine in the Debian context
  when *all* the same rules that apply to all contributions are also consistently applied to AI-assisted
  contributions. It describes how the same legality, accountability, no bulk change and privacy requirements
  are already in place and still apply and how AI-assisted contributions can and must still satisfy them. I could
  add again that some guidance would be nice here for both legal and environmental decisions when using AI,
  but in this case it does not really belong in this proposal itself. We as Debian do not have a document that
  requires that our non-AI-assisted contributions be made with only sustainably sourced electricity, for example.
  So why should AI be special one way or another? IMHO Debian *should* have a datacenter sustainability policy,
  regardless of the AI discussion.

* Proposal F - Action: discourage AI, but allow it based on existing processes (similar idea to E). Dances a bit
  around the question of disclosure of AI use (as a courtesy) and accepting that some people may still ban
  all contributions where any AI was involved in any way. Which in turn discourages disclosure to avoid pointless
  rejection of valuable contributions (like security patches). IMHO this option is ok, but so watered down that
  it is bound to bring up further discussions and conflicts on details.

* Proposal G - Action: ban non-humans from *directly* contributing to Debian. IMHO - another bizarre and
  self-contradictory option. It bans *all* Debian interactions with AI assistance, including email messages to
  Debian mailing lists and (supposedly) blog posts on Planet Debian. It "reminds" people who "use such tools
  assistively" of the DFSG and Social Contract - isn't that a threat of a ban and expulsion similar to C? The
  proposal does take pains to delineate where a contribution comes from AI as output (bad) vs when you are
  assisted by AI in the process of exploring, researching or maybe even reviewing the code, but you
  actually type all the code yourself and use the AI just as a taskmaster with a whip (good). And just like A
  or C it completely ignores how this inherently evil and unstable AI-generated code becomes perfectly fine and
  good as soon as someone develops that *outside* of the Debian project. Even if the same person then packages
  it for Debian the next day. It is hypocritical, unsustainable and ignores the needs of our users. Just like
  C it also bans someone writing an email or bug report in their native language and using a modern translation
  tool or service (that uses LLMs nowadays for better grammatical clarity) to translate that to English before
  sending it to a Debian mailing list or BTS. Heavy-handed and invasive. And the only reasoning provided
  for this is some unnamed "concerns" of "extra work" being borne by "other people"? Kind of does not feel
  right to bear such draconian restrictions for some unspecified concerns.

* Proposal H - Action: *condemn* usage, but not *actually* ban anything. And then it goes on to claim
  (without any evidence or elaboration) that LLM usage accelerates the destruction of "planet earth" (sic).
  IMHO this proposal is at the same time the loudest ("The planet is burning") and also the one that demands the
  *least* action. It dances a really twisty line between raising "significant" concerns in all areas and even
  claiming that use of LLMs destroys the planet, flies by explicit condemnation of LLM usage and then suddenly
  collapses with not condemning LLM users and swinging to lamentations that it is actually impossible to impose
  policies on LLM usage or even detect when an LLM was used (which kind of directly contradicts bad quality
  claims from A, C and G) and lands on "encouraging" contributors not to use LLMs (where practical) and otherwise
  do nothing else. It's like this is a 5th draft that started off with the rationale and total ban like in C,
  but then got defanged so far that its action side no longer matches the rationale stated.

With all the above considered I will vote like this (earlier options are preferred over later options):

* Proposal E - solid *hack* of integrating AI into already existing Debian rules and conventions
* Proposal B - explicit and detailed
* Proposal D - lower because of discouragement to others on what we agreed to do ourselves
* Proposal F - I am not a fan of dancing around with disclosures
* Further discussion - I do not want any option below this to succeed as they would do more harm than good
* Proposal H - loud, but not doing anything actually
* Proposal A - at least this one does not set rules for emails
* Proposal G - at least this one allows an AI overseer to tell you what to write with your own fingers
* Proposal C - the most draconic and invasive one that explicitly wants to kick people out of the project

Details on rationale

Hypocrisy - I find *any* proposal that would ban AI-assisted contributions to Debian, but at the same time *not*
ban including AI-assisted contributions from upstream projects to be inherently hypocritical. If LLMs
and AI are the very incarnation of evil (a puppy-killing machine, as the analogy went in some emails), then
any rational proposal would involve excluding any and *ALL* code contaminated by this evil from the project. What
does it matter if puppies were killed in writing the debian subfolder of the source code or the src subfolder?
No proposals went there because everyone knows that such a ban would be the death of the relevance of the project
for the future. Debian would be frozen on some old version of the Linux kernel forever and other software would be
falling to the same problem too, for example as projects on GitHub start enabling AI-supported reviews with patch
suggestions. Soon the "development" of Debian could just be stopped as there is nothing to develop without any
upstreams.

Assumptions - a lot of proposals mention various "concerns" with at most one word, like "practical" or "community"
without an explanation of what *exactly* they mean by that. The proposers assumed that everyone lives in the same info
bubble as they do and already know everything that they mean and already agree to that. That is false.
Proposal A was a positive stand-out in this area. Debian has contributors all over the world with very different
exposure to different information sources and very different world views. If you want to convince the project as a
whole that LLMs are bad because of "ethics", then you *do* really need to explain what you mean by that and give
links to sources, at least as well as Proposal A did. All other proposals were really weak in this area.

Copyright - the question on how copyright law interacts with training LLMs and their outputs is still not settled
law. The closest legal statements we have so far are that - just because an LLM is trained on copyrighted material
does *not* make that LLM itself be a derivative work of the training data (you, however, cannot just create and
distribute a "library" of copyrighted materials just because you plan to train LLMs on it). The output of the LLM
*might* not be subject to copyright law at all, like a photo taken by a monkey. It would then be public domain and
thus can be modified and then licensed by the user of the LLM. It *might* also be a derived work of the *context*
of the inference (so for software - if you refactor a GPL project, the refactoring itself is likely GPL too).
Any stricter interpretations would break a lot of existing copyright doctrine, such as raising questions like:
"does the output of any programmer now become a derived work of the programming manual books they read in college?".
In any case it is really not up to Debian to legislate the nuances of copyright law. And I strongly disagree with
the concept that an author can tell me how I am allowed to use the learnings that I gained by reading their work.
That is not how either copyright or society works. I can look at 10 pictures of a sunset and draw my own,
inspired by the ones I saw. No one can forbid me that expression. The same must be true for a machine learning and
replicating patterns.

Ethics - I've re-read all proposals and emails and the only real specifically ethical concern I could find was
the complaint that some LLMs (or their training farms) are running their web scrapers too aggressively and that
causes extra load on services. Like that is not an LLM problem. Scraping the web is not an inherent part of
the LLM training or inference process. It's just a few misconfigured scripts. We saw the exact same thing in the
early days of web search engine proliferation. Then we banned/blocked the misconfigured engines and the
survivors learned that obeying robots.txt is one of the rules for surviving. Literally the exact same problem
and it will be solved the same way. Did we ban all search engines back then just because some of them were
misconfigured? No.

Some claims (like in Proposal C) are just bombastic hyperbole ("hazards to users' mental health", "fraud", ...)
and on top of that have zero relevance to the topic at hand - AI-assisted contributions to Debian. What
"hazard to users' mental health" is created when a Coderabbit spots that a lock is not taken before accessing
a resource in a particular function and suggests an AI-generated patch to fix it? What "fraud" is committed by
this? There is no sane answer. I get that some people are very busy fighting some culture wars and sometimes,
some AI-bros happen to be on the other side of one such war, so it is useful to label everything coming
from the AI sphere as "bad" in all possible and impossible ways. You do you. In private. Why pull Debian into
that? Why force your position on everyone else in the project? Why deny everyone in the project access to
useful tooling, just because you have strong feelings about some of the people promoting some of those tools?

This seems to me a repeating pattern here - blaming the technology as a whole or blaming *all* providers
of this type of technology for failings (ethical or technical) of *some* of those providers. Like refusing
to wear *all* shoes and condemning all shoemakers and sellers, just because *some* American billionaires figured
out a way to make and sell cheap shoes by killing puppies. Not refusing and condemning *those* providers,
but condemning *all* for the actions of a *few*.

Resource usage - this is a big topic for many and it has reasonable points to it. The LLM and AI technology
has no *inherent* need to be damaging to the environment in any way for it to function. It does not need to
burn oil or dig up cobalt. It does not need to sacrifice a ton of water to the Gods. It is perfectly
possible to run AI (both inference and training) purely from green, electrical energy and cool data centers
in equally sustainable ways, like with simple air-source heat pumps (also known as air conditioning) or even
use it beneficially (many data centers are used for heating surrounding buildings via district heating).
However, *some* AI companies *do* use non-green power for their data centers, some do use locally-limited
fresh water for evaporative cooling (evaporated water still rains down as rain, it is not really lost, but
that may happen in another location so lack of water can still happen locally). Some even run unlicensed
natural gas turbines in their data centers to provide them with power. And those specific providers can
and should be shunned and condemned. Not the other ones, who are doing the right things. Not the technology
or its users or its outputs.

There is a *very* wide spectrum of options on how an AI system could be powered: starting from local execution
on already existing private hardware powered by one's own local solar power (good), to a data center stuffed with
borrowed AI-only cards powered by a gas turbine or coal power station that operates *solely* to supply this
data center (bad). Proposals that talk about ecological impact, but do not even consider where on that (very
wide) spectrum to draw the line between "good", "acceptable", "discouraged" and "bad" — well, I cannot see
those proposals being *actually* serious about the environment to begin with. It feels like they just refer
to it for points.

And if we go into the power question deeper, well the grid dynamics and economics become very, very complex and
often also non-intuitive. Like, all large software companies with data centers (that also happen to provide
AI services), like Google, Meta, Apple, Microsoft and others do actually care about sustainability (in part
because their customers care and vote with their wallets) and so all of them use 100% green energy for their
data centers (including AI data centers) .... "on an annual scale". Wait, what does *that* mean?
Well, the electrical grid is special - the amount of electricity produced and consumed on the whole electrical
grid together has to match almost exactly every *second*. If there is just a single second where there is
significantly more energy consumed from the grid than is produced, the frequency will plummet and you get
a brownout and risk a grid collapse. The same is true in reverse - that causes a voltage swell. So grid operators
manage energy flows every second and command power stations to increase and decrease generation all the time.
Some power stations are easier to regulate dynamically than others. In the end, all that means is that
even if your data center has a contract for 100% green energy with your power company, at *some* seconds
across the year there might not be enough green energy in the grid to fully supply ALL people and companies
that have 100% green energy contracts. This gets compensated in other seconds, so that across the year
("on an annual scale") for each kWh that your data center pulled from the grid, the same amount of kWh of
100% green energy flows into the grid. But it *might* not happen at the exact same second. Pedantic
companies, like Google, take that discrepancy and count that as CO2 emissions for themselves. And then
they and the power companies (they have contracts with) invest billions into new green energy projects,
better grids and better batteries so that *eventually* this discrepancy goes down to zero. In this way
green AI data centers with their increasing consumption of green energy are *actually* doing a lot
of good work in making our electrical grid *more* green. They are making more resources than they are
consuming. And that is just the tip of the iceberg. This is a *deep* topic that really abhors generalizations
like "more consumption = bad".

I've heard similar discussions in the context of electric cars - "so you got an electric car? you'd have fewer
emissions if you drove no car at all!". That might be so. And I would also reduce my emissions to zero
if I stopped breathing, but I *really* do not want that kind of thinking to be propagated further, especially
when impressionable young people are around who may take it to its logical (but wrong!) conclusion. Instead
I talk about how early adopters use electric cars to gather experience and achieve volume to start the
network effects working. Once network effects of many electric cars on the roads are sufficient, it becomes
an economically logical choice to get an electric car. People who *cannot* avoid having a car start
to switch over. And at the point of mass switchover the reduction of emissions is so massive that those
early adopters failing to go all the way to riding a bicycle becomes a rounding error.

But surely that does not apply to LLMs? They are only increasing consumption and bring no benefit?

Benefit - and here we have to actually talk about benefits. Because you cannot make any cost-benefit
analysis if you do not *actually* fully investigate the benefits. Are there environmental benefits from
running those AI models? Yes, in a lot of very diverse ways. Hard to measure, however. There are projects
that are easy to quantify - like that Google AI project on contrail avoidance. An advanced, special model
trained and executed in Google AI data centers was able to predict where in the air contrails would be
produced and could generate proposed course adjustments to commercial flights to avoid specific heights
in specific locations at specific times. This stopped these aircraft from creating contrails and those
contrails did not make a further contribution to global warming. That benefit in a year was many times higher than
the environmental cost of training and running that AI model. And it can keep running for many years
accumulating further benefits.

On a personal scale, I've had problems that I bashed my head (and computer
and CI resources) against without much success years ago solved with a few minutes of compute. Having
a good enough candidate solution quickly is *much* cheaper from a resource perspective than spending days
trying different things, running my PC for it, trying different patches on CI executions, doing different
rebuilds. I've seen very significant benefits in AI-assisted development in enterprise environments
where code way more complex than what is in Debian (especially in Debian tools and packaging) gets
analysed, reviewed, modified or even refactored or rewritten in another language with AI assistance.
And it generally works. The commonly mentioned "hallucinations" are a thing of last year in the coding
context. Nowadays the AIs work in special coding harnesses and use real tools as foundational facts.
You cannot "hallucinate" an API call or parameter if you have to run and pass the unit tests and
integration tests by your harness before you can return "success" to the caller. I've personally
seen high-level AI models read very complex software projects across multiple repositories and point
out a very specific design consideration that was encoded in the code logic, but never mentioned in
comments or documentation. It was so obscure that even I did not immediately know what it was
talking about (and I wrote that code). Only on close inspection of code interaction across three repos
did I remember that there was indeed that bug 2 years ago that I fixed by doing the change that
this AI picked up (it wasn't in the history of this git repo due to repo migration). It mentioned
this because it was very relevant to the task I initially gave it to review.

These LLMs in a proper harness with proper system instructions and usage approach are not just fancy
spell checkers or auto-complete. They function more like very advanced pattern matchers. They have learned
millions of patterns from training data. When they look at the code, they see hundreds or thousands of
overlapping patterns. When you ask them to make or change something, they pull out a pattern (or ten)
from their training and apply those patterns to the context of your program. You get something that
looks just like the surrounding code, same style choices, same language, same comment voice, but it
implements something new there, based on other patterns learned. If you've studied design patterns
in your CS class, this will be familiar. But people can learn and remember maybe 20-30 patterns, while
an LLM can have a million patterns and can combine them when needed. So it takes a pattern of
Python code, pattern of standalone script, pattern of parsing command line parameters, pattern of
classes, pattern for background threads, pattern for file tree traversing, pattern for pipes, ... and
squishes them together to make a solution for your query. And then tries to debug it with compilation,
tests and execution until it works as expected. Even if there is zero LLM development going forward, it
will take many years to fully appreciate the benefits we can extract from the already trained models.
They don't even have to be retrained - for existing languages they just keep working. For new
language variations, like a new Python version, you can feed the changelog into context and they will
be able to work with a Python version that they never saw in training. And patterns are mostly abstract,
so not really specific to any language - human or programming.

This is another big enabler that LLMs have created that we have not really explored yet. LLMs have
created *really* free software. People can *actually* create software that is perfectly suited just
for them and no one else. They don't even have to know how to program and don't even need to speak
English. I've seen people writing prompts in their native language and LLMs creating and then adjusting
web apps or Android/iPhone apps and deploying them to the user's own phone. It was too buggy to work last
year, but this year it is actually very functional for simpler use-cases. And the code looks just
fine too - I've seen external contractors in a business setting deliver far worse. If you start with
a good initial system prompt, the project will have architecture documentation, use-case documentation,
unit tests, integration tests, deployment harness, testing and production deployments, audit logs,
monitoring, clear git commits, CI validation on commit, ... Modern AI systems have the capabilty
to deliver software freedom to people who are not coders. I really can not overstate the consequences
this may have on the world.

Community - I find the concerns that new people will be using LLMs so much that they will no longer
be understanding the actual code they are contributing a bit regressive. I don't see any significant
difference between this and people relying on compilers, on high-level languages or on debhelper.
Writing modern debhelper packaging feels more like writing configuration and not writing code. It
takes really significant effort to dig down through layers of abstraction to find what *actually*
is being executed in debian/rules. AI does not really make this worse. In fact, I find that AI
can make it much easier to understand arcane syntax because you can ask an LLM to *explain* what is
happening in any part of the code and it will do a pretty good job of it, digging down through
the layers of abstraction for you. All the pro-AI proposals include the requirement that each
*human* contributor needs to understand and stand behind their AI-assisted contribution and I
believe that is a good requirement and also a sufficient requirement. Modern LLMs not only produce
clear and concise code, but they are also capable of producing good comments explaining why the
code is how it is, good commit messages explaining the change and reason behind it and also
making corresponding changes to test suites and documentation. You know - the housekeeping stuff
that is often skipped because it slows down the actual feature development, but then its lack
becomes a problem for future contributors. Responsible use of AI assistance is a great chance
to actually *strengthen* our community and make our software easier to maintain.

That said, I have no qualms about flat-out rejecting contributions that do not make sense. And
it does not matter if they are made with or without AI assistance. If the contributor will not
explain their patch, it might be they do not understand what their AI produced *or* it could be
that the contribution is deliberately hiding a backdoor being planted. It is also quite common
for a contribution of a new feature to be rejected because the author/maintainer does not believe
that it is a good fit for the project. Featuritis is a real disease. AI or not. There have always
been drive-by contributions to various projects. They will continue to exist. Each of them should
be evaluated on its merits - is this feature valuable to our users and is the added complexity
(if any) worth the functionality? A lot of security bug reports are "drive-by" contributions as
well. And many of them nowadays are discovered, exploited and patched with AI assistance. We
could reject them, but that just leaves us holding the bag on the now-known exploits.

And the New Maintainer process should be able to figure out if an upcoming Developer has actually
understood the nuances of Debian packaging or not. A contributor with upload rights to the
archive *has to* be able to create a basic package with no support tooling (maybe even without
using debhelper?) and be able to understand and modify more complex packages (possibly with
tooling support). IMHO that is a separate discussion that is worth having, involving experts from
the educational sector.

Conclusion

IMHO the Debian project should not restrict what tooling individual contributors use to contribute.
Expecting high-quality contributions and that contributors understand what they are contributing
(as a first level of review) is enough.

However, Debian should provide its contributors (internal or external) with guidance on *how*
to contribute in the best way possible. That could include:

* information on which AI services have Terms and Conditions that make them problematic for free
  software development, legally speaking
* information on which AI services do (or do not) achieve a sufficient level of sustainability to be
  worth recommending (and then do the same for other data centers we already use)
* information on which local AI models were trained in sustainable ways
* base-level prompts to set technical expectations on various types of contributions, like bug
  reports or patches to packaging or translations
* default configuration for AI-assisted code reviews on Salsa that projects could enable and
  supplement with their own instructions on top

In addition to that it would be helpful for Debian, as a project, to reach out to AI service
providers to:

* encourage them to improve sustainability (where needed)
* investigate and fix problems causing excessive scraping load on systems
* provide AI resources for Debian usage, for example in CI infrastructure or to provide equal
  development support opportunities for Debian developers who cannot afford paid AI services
* improve coding outputs of their models in the Debian context if/when systematic deficiencies
  in the output are found by us

Questions? Feedback? Just ask
[here](https://bsky.app/profile/aigarius.com/post/3mtql3ologs2p) or
[here](https://www.threads.com/share/DXreYglXv/).