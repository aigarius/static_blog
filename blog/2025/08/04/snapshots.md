<!--
.. title: Snapshot mirroring in Debian (and Ubuntu)
.. slug: snapshot-mirrors
.. date: 2025-08-04 18:00:00 UTC
.. tags: Debian-planet,Ubuntu.lv-planet,blog,travel,debian,photo
.. category:
.. link:
.. description:
.. type: text
-->

# Snapshot mirroring in Debian (and Ubuntu)

The use of snapshots has been routine in both [Debian](http://snapshot.debian.org) and [Ubuntu](http://snapshot.ubuntu.com) for several years now—or more than 15 years for Debian, to be precise. Snapshots have become not only very reliable, but also an increasingly important part of the Debian package archive.

This week, I encountered a problem at work that could be perfectly solved by correctly using the Snapshot service. However, while trying to figure it out, I ran into some shortcomings in the documentation. Until the docs are updated, I am publishing this blog post to make this information easier to find.

**Problem 1:** Ensure fully reproducible creation of Docker containers with the *exact* same packages installed, even *years* after the original images were generated.

**Solution 1:** Pin *everything*! Use a pinned source image in the `FROM` statement, such as `debian:trixie-20250721-slim`, and also pin the APT package sources to the "same" date - "20250722".

*Hint:* The APT packages need to be *newer* than the Docker image base. If the APT packages are a bit newer, that's not a problem, as APT can upgrade packages without issues. However, if your Docker image has a newer package than your APT package sources, you will have a *big* problem. For example, if you have "libbearssl0" version 0.6-2 installed in the Docker image, but your package sources only have the older version 0.6-1, you will fail when trying to install the "libbearssl-dev" package. This is because you only have version 0.6-1 of the "-dev" package available, which hard-depends on *exactly* version 0.6-1 of "libbearssl0", and APT will refuse to downgrade an already installed package to satisfy that dependency.

**Problem 2:** You are using a *lot* of images in a *lot* of executions and building tens of thousands of images per day. It would be a bad idea to put all this load on public Debian servers. Using local sources is also faster and adds extra security.

**Solution 2:** Use local (transparently caching) mirrors for both the Docker Hub repository and the APT package source.

At this point, I ran into another issue—I could not easily figure out how to specify a local mirror for the *snapshot* part of the archive service.

First of all, snapshot support in both Ubuntu and Debian accepts both syntaxes described in the Debian and Ubuntu documentation above. The documentation on both sites presents different approaches and syntax examples, but both work.

The best approach nowadays is to use the "deb822" sources syntax. Remove /etc/apt/sources.list (if it still exists), delete all contents of the /etc/apt/sources.list.d directory, and instead create this file at /etc/apt/sources.list.d/debian.sources:

```text
Types: deb
URIs: https://common.mirror-proxy.local/ftp.debian.org/debian/
Suites: trixie
Components: main non-free-firmware non-free contrib
Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg
Snapshot: 20250722
```

Hint: This assumes you have a mirror service running at common.mirror-proxy.local that proxies requests (with caching) to whitelisted domains, based on the name of the first folder in the path.

If you now run `sudo apt update --print-uris`, you will see that your configuration accesses your mirror, but does not actually use the snapshot.

Next, add the following to /etc/apt/apt.conf.d/80snapshots:

```text
APT::Snapshot "20250722";
```

That should work, right? Let's try `sudo apt update --print-uris` again. I've got good news and bad news! The good news is that we are now actually using the snapshot we specified (twice). The bad news is that we are completely ignoring the mirror and going directly to snapshots.debian.org instead.

Finding the right information was a bit of a challenge, but after a few tries, this worked: to specify a custom local mirror of the Debian (or Ubuntu) snapshot service, simply add the following line to the same file, /etc/apt/apt.conf.d/80snapshots:

```text
Acquire::Snapshots::URI::Override::Origin::debian "https://common.mirror-proxy.local/snapshot.debian.org/archive/debian/@SNAPSHOTID@/";
```

Now, if you check again with `sudo apt update --print-uris`, you will see that the requests go to your mirror *and* include the specified snapshot identifier. Success!

Now you can install any packages you want, and everything will be completely local and fully reproducible, even years later!
