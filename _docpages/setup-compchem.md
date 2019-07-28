---
layout: inner
title: How to compile things
image: images/disco_dingo.jpg
featured: false
comments: true
sidebar:
  nav: pages/setup-compchem
---


A log of the installation dependencies and processes of annoying packages, as well as said packages.

# GROMACS

## 2016.1
This requires cuda 8.0, which requires gcc 5.

### Installing GCC
You can mostly find gcc 6+ in the Disco Dingo repository and install them with `apt install gcc-8` etc. However, older versions require a bit more effort.

#### GCC 5.4
Download the source from the GCC website. Unpack it and make a build directory ([instructions copied from the GCC website](https://gcc.gnu.org/wiki/InstallingGCC)):

```console
tar xzf gcc-5.4.0.tar.gz
cd gcc-5.4.0
./contrib/download_prerequisites
cd ..
mkdir objdir
cd objdir
```
Now you need to modify `libgcc/config/i386/linux_unwind.h` to change two instances of `struct ucontext *uc_` to `struct ucontext_t *uc_`. In GCC 6.4 these were on lines 61 and 141, but there may be minor differences. (This is not required for the patched version available on our shared drive, O'Mara group readers.)

Now configure and checkinstall. I've configured this to install on a hard drive mounted at `/store`, but you can equally install it in your home directory or elsewhere.
```console
$PWD/../gcc-5.4.0/configure --prefix=/store/opt/gcc-5.4.0 --enable-languages=c,c++,fortran --disable-multilib
make
sudo checkinstall
```
**Make sure your checkinstall package has a version number, or it'll fail!**

At this point you may wish to set up `update-alternatives` for easy switching between compilers. You may not have all the gcc's below – if you do need them, `sudo apt install gcc-6 g++-6 gcc-7 g++-7` will do it (as of 2019). The lines below clear the alternatives you already have, and then configure the program path (second last field, eg `/store/opt/gcc-5.4.0/bin/gcc`) to the first field (eg `/usr/bin/gcc`) with the priority of the last number. A larger number indicates a higher priority. 
```console
sudo update-alternatives --remove-all gcc
sudo update-alternatives --remove-all g++
sudo update-alternatives --install /usr/bin/gcc gcc /store/opt/gcc-5.4.0/bin/gcc 10
sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-6 20
sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-7 30
sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-8 40
sudo update-alternatives --install /usr/bin/g++ g++ /store/opt/g++-5.4.0/bin/gcc 10
sudo update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-6 20
sudo update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-7 30
sudo update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-8 40
```

To switch between them:
```console
sudo update-alternatives --config gcc
```

### Installing CUDA
Make sure you have the patched version of `cuda_8.0.61_375.25_linux.run`. Unpack this and copy `InstallUtils.pm` to your computer.
```console
./cuda_8.0.61_375.25_linux.run --tar mxvf
sudo cp InstallUtils.pm /usr/lib/x86_64-linux-gnu/perl-base
export $PERL5LIB
```
You can run through this interactively or with flags. If you remove the flags below, the interactive installer will come up. We only want to install the toolkit (nothing else), to the path specified. 
```console
sudo sh cuda_8.0.61_375.25_linux.run --toolkit --toolkitpath=/packages/cuda/cuda-8.0 --silent
```
Check to see that `packages/cuda/cuda-8.0/bin/nvcc` exists.

### Installing GROMACS
Make sure you have `cmake` installed. You can get this with `sudo apt install cmake`. 
#### Process
```console
lily@gavle:$ tar xfz gromacs-2016.1.tar.z
lily@gavle:$ cd gromacs-2016.1
lily@gavle:$ mkdir build && cd build
lily@gavle:$ cmake .. -DGMX_BUILD_OWN_FFTW=ON -DREGRESSIONTEST_DOWNLOAD=ON -DGMX_GPU=on -DCMAKE_INSTALL_PREFIX=/packages/gromacs/gromacs-2016.1 -DCMAKE_CXX_FLAGS=-fPIC -DCUDA_TOOLKIT_ROOT_DIR=/packages/cuda/cuda-8.0
lily@gavle:$ make -j 6
lily@gavle:$ make check
lily@gavle:$ sudo checkinstall
```

## 2018.3
This is a lot easier.

#### Process
```console
lily@gavle:$ cmake .. -DGMX_BUILD_OWN_FFTW=ON -DREGRESSIONTEST_DOWNLOAD=ON -DGMX_GPU=on -DCMAKE_INSTALL_PREFIX=/packages/gromacs/gromacs-2018.3 -DCMAKE_CXX_FLAGS=-fPIC -DCUDA_TOOLKIT_ROOT_DIR=/packages/cuda/10.1
lily@gavle:$ make -j 6
lily@gavle:$ make check
lily@gavle:$ sudo checkinstall
```

<a name="amber"/>

# AMBER

## Amber16
This is the version we have the license for, but I imagine they're all similar.

## AmberTools 19
### Dependencies

gcc=8.3.0

cuda=10.1

```console
lily@gavle:$ gcc --version
gcc (Ubuntu 8.3.0-6ubuntu1) 8.3.0
Copyright (C) 2018 Free Software Foundation, Inc.
This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

lily@gavle:$ nvcc --version
nvcc: NVIDIA (R) Cuda compiler driver
Copyright (c) 2005-2019 NVIDIA Corporation
Built on Fri_Feb__8_19:08:17_PST_2019
Cuda compilation tools, release 10.1, V10.1.105
```

### Process
```console
lily@gavle:$ cd /packages/amber/18
lily@gavle:$ ./configure -cuda gnu
lily@gavle:$ sudo checkinstall
```

**Note:** I ran into trouble with AMBER not finding $CUDA_HOME. After you've made sure it is set with echo $CUDA_HOME, one solution is:

```console
lily@gavle:$ echo $CUDA_HOME && checkinstall
```

However, if you are installing at a system level and require root permissions, `echo $CUDA_HOME && sudo checkinstall` *did not* work for me. The only way to get around it was to start a root session.

```console
lily@gavle:$ sudo su
root@gavle:$ export CUDA_HOME=/packages/cuda/10.1
root@gavle:$ echo $CUDA_HOME && checkinstall
```

I also symlinked `/bin/cpptraj.cuda` to `/bin/cpptraj` .

# Visualisation programs
## VMD
This is quite straightforward; the only key is making sure you have CUDA loaded if you have that turned on in your configuration options.

```console
cd vmd-1.9.3
./configure
cd src
sudo checkinstall
```
## Pymol
```console
sudo apt install pymol
```
This may cause issues with Anaconda. Alternatively, you can register for an educational license and download the commercial version of Pymol 2.0.

```console
conda install -c schrodinger pymol
```
The Schrodinger pymol is the commercial one. This gave us less than a year before needing renewal and the program segmentation faulted when I double-clicked, so I went for EduPymol 1.7.4. This should be downloaded from the Schrodinger site after registering for an educational account. I moved the download to `/packages/pymol/pymol-1.7.4` and symlinked pymol to `/usrlocal/bin`.
```console
sudo ln -s /packages/pymol/pymol-1.7.4/pymol /usr/local/bin/
```

# Other
## Autodock