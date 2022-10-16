<!--
.. title: Ryzen 7000 amdgpu boot hang
.. slug: ryzen-7000-amdgpu
.. date: 2022-10-16 14:15:13 UTC
.. tags: Debian-planet,Ubuntu.lv-planet,hardware,debian
.. category:
.. link:
.. description:
.. type: text
-->

So you decided to build a brand new system using all the latest and coolest tech, so you buy a Ryzen 7000 series
Zen 4 CPU, like the Ryzen 7700X that I picked, with a new mother board and DDR5 memory and all that jazz. But for
now, you don't yet have a fitting GPU for that system (as the new ones will only come out in November), so you are
booting a Debian system using the new build-in video card of the new CPUs (Zen 4 generation has a simple AMD GPU
build-in into every CPU now - great stuff for debugging and mostly-headless systems) and you get ... nothing on 
the screen. Hmm. You boot into the rescue mode and the kernel message stop after:

```
Oct 16 13:31:25 home kernel: [    4.128328] amdgpu: Ignoring ACPI CRAT on non-APU system
Oct 16 13:31:25 home kernel: [    4.128329] amdgpu: Virtual CRAT table created for CPU
Oct 16 13:31:25 home kernel: [    4.128332] amdgpu: Topology: Add CPU node
```

That looks bad, right?

Well, if you either ssh into the machine or reboot with `module_blacklist=amdgpu` in the kernel command line you will 
find in `/var/log/kern.log.1` those messages and also the following messages that will clarify the situation a bit:

```
Oct 16 13:31:25 home kernel: [    4.129352] amdgpu 0000:10:00.0: firmware: failed to load amdgpu/psp_13_0_5_toc.bin (-2)
Oct 16 13:31:25 home kernel: [    4.129354] firmware_class: See https://wiki.debian.org/Firmware for information about missing firmware
Oct 16 13:31:25 home kernel: [    4.129358] amdgpu 0000:10:00.0: firmware: failed to load amdgpu/psp_13_0_5_toc.bin (-2)
Oct 16 13:31:25 home kernel: [    4.129359] amdgpu 0000:10:00.0: Direct firmware load for amdgpu/psp_13_0_5_toc.bin failed with error -2
Oct 16 13:31:25 home kernel: [    4.129360] amdgpu 0000:10:00.0: amdgpu: fail to request/validate toc microcode
Oct 16 13:31:25 home kernel: [    4.129361] [drm:psp_sw_init [amdgpu]] *ERROR* Failed to load psp firmware!
Oct 16 13:31:25 home kernel: [    4.129432] [drm:amdgpu_device_init.cold [amdgpu]] *ERROR* sw_init of IP block <psp> failed -2
Oct 16 13:31:25 home kernel: [    4.129525] amdgpu 0000:10:00.0: amdgpu: amdgpu_device_ip_init failed
Oct 16 13:31:25 home kernel: [    4.129526] amdgpu 0000:10:00.0: amdgpu: Fatal error during GPU init
Oct 16 13:31:25 home kernel: [    4.129527] amdgpu 0000:10:00.0: amdgpu: amdgpu: finishing device.
Oct 16 13:31:25 home kernel: [    4.129633] amdgpu: probe of 0000:10:00.0 failed with error -2
```

So what you need is to get a new set of [Linux Kernel Firmware blobs](https://git.kernel.org/pub/scm/linux/kernel/git/firmware/linux-firmware.git) and upack that in `/lib/firmware`. 
The tarball from 2022-10-12 worked well for me.

After that you also need to re-create the initramfs with `update-initramfs -k all -c` to include the new firmware. 
Having kernel version 5.18 or newer is also required for stable Zen 4 support. It might be that a fresh Mesa version
is also of importance, but as I am running sid on this machine I can only say that Mesa 22.2.1 that is in sid works fine.
