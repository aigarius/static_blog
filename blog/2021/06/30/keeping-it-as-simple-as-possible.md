<!--
.. title: Keeping it as simple as possible
.. slug: keeping-it-as-simple-as-possible
.. date: 2021-06-30 19:49:59 UTC
.. tags: Debian-planet,Ubuntu.lv-planet,blog,software
.. category:
.. link:
.. description:
.. type: text
-->

You know that you've had the same server too long when they discontinue the
entire class of servers you were using and you need to migrate to a new
instance. And you know you've not done anything with that server (and the blog
running on it) for too long when you have no idea how that thing is actually
working.

Its a good opportunity to start over from scratch, and a good motivation to the
new thing as simply as humanly possible, or even simpler.

So I am switching to a statically generated blog as well. Not sure what took me
so long, but thank good the tooling has really improved since the last time I
looked.

It was as simple as picking Nikola, finding its import_feed plugin, changing the
`BLOG_RSS_LIMIT` in my Django Mezzanine blog to a thousand (to export all posts
via RSS/ATOM feed), fixing some [bugs](https://github.com/getnikola/plugins/issues/389)
in the import_feed plugin, waiting a few minutes for the full feed to generate
and to be imported, adjusting the config of the resulting site, posting that to
[git](https://github.com/aigarius/static_blog) and writing a simple shell script
to pull that repo periodically and call `nikola build` on it, as well as config
to serve ther result via ngnix. Done.

After that creating a new blog post is just `nikola new_post` and editing it in
vim and pushing to git. I prefer Markdown, but it supports all kinds of formats.
And the old posts are just stored as HTML. Really simple.

I think I will spend more time fighting with Google to allow me to forward email
from my domain to my GMail postbox without it refusing all of it as spam.
