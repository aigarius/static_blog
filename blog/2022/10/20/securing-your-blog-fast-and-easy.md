<!--
.. title: Securing your blog - fast and easy
.. slug: securing-your-blog-fast-and-easy
.. date: 2022-10-20 20:04:50 UTC
.. tags: blog,software,Debian-planet,Ubuntu.lv-planet,debian
.. category: 
.. link: 
.. description: 
.. type: text
-->

After the last couple of posts a few people asked me why my blog site is still HTTP-only? Why did I not
secure my page and contribute my little bit to normalizing encrypted traffic on the Internet and all
that good jazz?

And the answer was - I was lazy and thought that it was complicated.

I could not have been more wrong :D However the key here is *not* to follow the *official* guides.
In fact doing things the *Debian way* turned out to be far simpler and straight forward.

If you want to get a free SSL certificate and setup your site correctly, you will likely eventually
get to [this page](https://certbot.eff.org/instructions) and it will then you instrct you to install
snap and pull a snap package of certbot. Well, no. I will not be doing that, thank you very much.
I have a perfectly functional Debian packaing system right here and I do not want to pollute my system
with multiple package managers and updaters. No snap, no flatpack. I am fine with Docker because those
are containers, they are *not* in my system, they run in separated systems above my system.

Turns out all of that was way more complicated than necessary, anyway.

Debian Buster contains a perfectly functional package of certbot and it is fully integrated too!

All I had at the start was my domain configured on HTTP in nginx.

All I did was:

```
# apt install certbot python3-certbot-nginx
# certbot run
```

It asked me a few questions about me, which domain to work on (of the configured nginx domains that it 
automatically found) and then just automagically got the certificates, deployed them and configured nginx 
to enable HTTPS using those new certificates. As an extra it also asked me if I wanted to redirect all 
HTTP traffic to HTTPS and that was it. I was done. No extra steps, no config files edited, no complex 
command lines and no extra package managers installed on my system.

10/10 would recommend!

Edit: it looks like the certbot handled the "aigarius.com" domain perfectly, *but* missed the redirects 
from "www.aigarius.com", so I'd have to fix those up manually by just copying the directive that certbot
added to nginx config file for "aigarius.com" and editing the domain name.
