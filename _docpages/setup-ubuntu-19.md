---
layout: inner
title: How to set-up Ubuntu 19.04
image: images/disco_dingo.jpg
featured: false
comments: true
sidebar:
    nav: setup-ubuntu-19.md
---

Here is how to set up Ubuntu 19.04 on a computer to work, the first time. 

# Basics

## 0. Obtain a Ubuntu USB drive

You need to somehow create a bootable USB stick. This is easiest in Ubuntu and there are many tutorials already, so I won't clutter it up.

## 1. Install Ubuntu and drivers

Stick the USB in and boot up the computer. You need to change the boot order to boot off the USB stick first. This differs across operating systems; on our old Ubuntu 16.04s, we hit F10 to bring up Boot Options.

You can choose a normal installation or a minimal one. Out of convenience, we go with the normal installation; the only weirdly irritating thing it installs is Amazon. This shouldn't take long -- ours was under 10 min. 

The computer will reboot after this.

**Do not reboot again before Step 3.**

## 2. Reconfiguring grub and the display server
```console
lily@gavle$ sudo apt upgrade
lily@gavle$ ubuntu-drivers autoinstall
```
These are most likely installed already, but you can check anyway:
```console
lily@gavle$ sudo apt install build-essential
lily@gavle$ sudo apt install linux-headers-$(uname -r)
```

We found that if we rebooted our computer off the *default* installation, the displays wouldn't work. It turns out this is *probably* because of the buggy Wayland display server, but we didn't sit down to disentangle Wayland vs. Nvidia drivers (another common source of issues) vs. buggy video drivers as a whole.

You may like to install vim.
```console
lily@gavle$ sudo apt install vim
```

Edit `/etc/gdm3/custom.conf` by uncommenting `# WaylandEnable=false`.
This will forces the computer to use the Xorg display server, ie the one that actually works.

Edit `/etc/default/grub`. Replace:
```console
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"
```
with
```console
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash nomodeset"
```
This will disable video drivers until the kernel has started.
Update with:
```console
lily@gavle$ sudo update-grub
```

**Still do not reboot before Step 3.**


## 3. Configure SSH
Before you reboot, set up SSH so you can get in if your displays die. This installs openssh-server, enables the service and starts the service.
```console
lily@gavle$ sudo apt install openssh-server
lily@gavle$ sudo systemctl enable ssh
lily@gavle$ sudo systemctl start ssh
```
Test your access by ssh-ing in. To set up a firewall, first check that this line `IPV6=yes` is in `/etc/default/ufw`. 
```console
lily@gavle$ sudo ufw default deny incoming
lily@gavle$ sudo ufw default allow outgoing
lily@gavle$ sudo ufw allow ssh
lily@gavle$ sudo systemctl start ufw
lily@gavle$ sudo systemctl enable ufw
```

### SSH keys
Later, you can set up SSH keys.
```console
lily@gavle$ ssh-keygen -t rsa -b 4096
```
To copy your details over to other places:
```
lily@gavle$ ssh-copy-id username@destination
```

# Extras
## 4. Checkinstall, GCC (optional)
### Checkinstall
[checkinstall](https://wiki.debian.org/CheckInstall) is a useful tool that replaces `make install`. It build a .deb package that is easily removable with:
```console
lily@gavle$ dpkg -r yourpackagename
```

```console
lily@gavle$ sudo apt install checkinstall
```


## 5. Environment modules
Install dependencies. Here the latest tcl-dev is 8.6, but check.
```console
lily@gavle$ sudo apt-get install tcl tcl8.6-dev
```

Download and unzip the latest [Environment Modules](http://modules.sourceforge.net/). Here it's 4.2.3. Navigate to the directory.
```console
lily@gavle$ cd modules-4.2.3/
```

Make folders to store the modulefiles and packages
```console
lily@gavle$ sudo mkdir /modules /packages
```

Set up the build, make, and checkinstall it.
```console
lily@gavle$ ./configure
lily@gavle$ make
lily@gavle$ sudo checkinstall
```
If `/etc/profile.d/modules.sh` and `/etc/profile.d/modules.csh` already exist, skip this step. Otherwise, copy or symlink them.
```console
lily@gavle$ sudo ln -s /usr/local/Modules/init/profile.sh /etc/profile.d/modules.sh
lily@gavle$ sudo ln -s /usr/local/Modules/init/profile.csh /etc/profile.d/modules.csh
```
Now, when you install applications, try to install them into /packages. Modulefiles are included in the repo for your convenience.

Note that the default path for modulefiles is `/usr/local/Modules/modulefiles`. Edit `/usr/local/Modules/init/modulerc` and add `module use /modules` to use the directory you made above.

## 6. Anaconda and Python
Download and install Anaconda **before** you do anything with Python. This will likely install Visual Studio Code as well, which is super helpful. Open a folder in VS Code with

```console
lily@gavle$ code .
```

### Environments
Create a new environment with 
```console
lily@gavle$ conda create --name myenv [python=3.6] [scipy=0.15.0]
```
Use the options in brackets if you need a specific version of Python and/or specific packages. You can also activate it and install directly into it.

<a name="step7"/>

# Computational chemistry stuff
<a href="{{ site.url }}/docpages/setup-compchem"> For information on compiling GROMACS, AMBER, and possibly other packages, go here.</a>