"use strict";
/* eslint-disable max-len, node/global-require */
const XU = require("@sembiance/xu"),
	fileUtil = require("@sembiance/xutil").file,
	path = require("path"),
	fs = require("fs"),
	tiptoe = require("tiptoe");

tiptoe(
	function findPrograms()
	{
		fileUtil.glob(path.join(__dirname, "..", "src", "program"), "**/*.js", {nodir : true}, this);
	},
	function generateReadme(programFilePaths)
	{
		const programs = programFilePaths.map(programFilePath => require(programFilePath));

		// bin/runServers.js
		programs.push({bin() { return "jq"; }, meta : {gentooPackage : "app-misc/jq", website : "https://stedolan.github.io/jq/"}});

		// server/qemu.js
		programs.push({bin() { return "qemu-system-*"; }, meta : {gentooPackage : "app-emulation/qemu", website : "http://www.qemu.org", gentooUseFlags : "aio alsa bzip2 caps curl fdt filecaps gtk jpeg lzo ncurses nls opengl oss pin-upstream-blobs png seccomp slirp spice usb usbredir vhost-net vnc xattr zstd"}});
		programs.push({bin() { return ""; }, meta : {gentooPackage : "x11-drivers/xf86-video-qxl", website : "https://gitlab.freedesktop.org/xorg/driver/xf86-video-qxl", gentooUseFlags : "xspice"}});
		programs.push({bin() { return "mount.cifs"; }, meta : {gentooPackage : "net-fs/cifs-utils", website : "https://wiki.samba.org/index.php/LinuxCIFS_utils", gentooUseFlags : "caps creds pam"}});
		programs.push({bin() { return "rsync"; }, meta : {gentooPackage : "net-misc/rsync", website : "https://rsync.samba.org/", gentooUseFlags : "acl iconv ipv6 ssl xattr zstd"}});
		
		// hashUtil.hash
		programs.push({bin() { return "b3sum"; }, meta : {gentooPackage : "app-crypt/blake3", website : "hhttps://github.com/BLAKE3-team/BLAKE3"}});

		// runUtil.run
		programs.push({bin() { return "Xvfb"; }, meta : {gentooPackage : "x11-base/xorg-server", website : "https://www.x.org/wiki/", gentooUseFlags : "libglvnd xorg xvfb"}});
		programs.push({bin() { return "hsetroot"; }, meta : {gentooPackage : "x11-misc/hsetroot", website : "https://wiki.gentoo.org/wiki/No_homepage"}});

		// videoUtil.info (and DOS video recording too)
		programs.push({bin() { return "mplayer"; }, meta : {gentooPackage : "media-video/mplayer", website : "http://www.mplayerhq.hu/", gentooUseFlags : "X a52 alsa cdio dga dts dv dvd dvdnav enca encode iconv joystick jpeg libass live lzo mad mng mp3 network opengl osdmenu png rtc shm tga theora truetype unicode v4l vcd vdpau vorbis x264 xinerama xscreensaver xv xvid"}});
		
		// unicodeUtils.fixDirEncodings
		programs.push({bin() { return "convmv"; }, meta : {gentooPackage : "app-text/convmv", website : "https://www.j3e.de/linux/convmv/"}});

		// dosUtil
		programs.push({bin() { return "dosbox"; }, meta : {gentooPackage : "games-emulation/dosbox", website : "http://dosbox.sourceforge.net/", gentooUseFlags : "alsa opengl"}});
		programs.push({bin() { return "xdotool"; }, meta : {gentooPackage : "x11-misc/xdotool", website : "https://www.semicomplete.com/projects/xdotool/"}});

		// python tensorflow server
		programs.push({bin() { return ""; }, meta : {gentooPackage : "sci-libs/tensorflow", website : "https://www.tensorflow.org/"}});
		programs.push({bin() { return ""; }, meta : {gentooPackage : "dev-python/flask", website : "https://github.com/pallets/flask/"}});
		programs.push({bin() { return ""; }, meta : {gentooPackage : "dev-python/pillow", website : "https://python-pillow.org/"}});

		const programCount = programs.length;

		programs.filterInPlace(p => p.meta.hasOwnProperty("gentooPackage"));

		// Some programs are nodejs scripts that call multiple gentoo packages and binaries (such as uniso)
		const multiProgs = programs.filter(p => Array.isArray(p.meta.gentooPackage));
		programs.filterInPlace(p => !Array.isArray(p.meta.gentooPackage));

		multiProgs.forEach(multiProg => programs.push(...multiProg.meta.gentooPackage.map((subGentooPackage, i) => ({ bin() { return multiProg.meta.bin[i]; }, meta : {kernel : multiProg.meta.kernel || undefined, gentooPackage : subGentooPackage, website : multiProg.meta.website[i] || ""} }))));

		fs.writeFile(path.join(__dirname, "..", "INSTALL.md"), `# WARNING
Over ${programCount} programs are required, including commercial programs and operating systems.
This isn't something you can easily get up and running in an afternoon.
		
# Install
\`npm install dexvert -g\`
		
# Requirements

## Kernel
Several kernel options need to enabled to support QEMU and mounting various fileystems dexvert may encounter.

\`\`\`
    General setup  --->
      <*> Control Group support  --->
            [*] Memory controller
            [*] Freezer controller
            [*] Cpuset Controller
            [*]   Include legacy /proc/<pid>/cpuset file
            [*] Simple CPU accounting controller

    Processor type and features --->
      [*] NUMA Memory Allocation and Scheduler Support

[*] Virtualization  --->
      <*> Kernel-based Virtual Machine (KVM) support
	  # Choose either Intel or AMD
      <*>   KVM for Intel (and compatible) processors support
	  <*>   KVM for AMD processors support

[*] Networking support  --->
    Networking options  --->
	  <*> 802.1d Ethernet bridging
	  [*]   IGMP/MLD snooping

    Device Drivers  --->
      [*] PCI support  --->
	        [*] Message Signaled Interrupts (MSI and MSI-X)
      [*] Network device support  --->
            [*]   Network core driver support
            <*>     MAC-VLAN support
            <*>       MAC-VLAN based tap driver
            <*>   Universal TUN/TAP device driver support
      [*] VHOST drivers  --->
            [*] Host kernel accelerator for virtio net
            [*] Cross-endian support for vhost
      [*] IOMMU Hardware Support  --->
	        # Choose either Intel or AMD
			[*] AMD IOMMU support
			<*>   AMD IOMMU Version 2 driver
            [*] Support for Intel IOMMU using DMA Remapping Devices
            [*]   Support for Shared Virtual Memory with Intel IOMMU
            [*]   Enable Intel DMA Remapping Devices by default

    File systems  --->
      <*> The Extended 4 (ext4) filesystem
	  [*]   Ext4 Security Labels
          CD-ROM/DVD Filesystems  --->
    	    <*> ISO 9660 CDROM file system support
    	    [*]   Microsoft Joliet CDROM extensions
    	    [*]   Transparent decompression extension
    	    <*>   UDF file system support
    	  DOS/FAT/EXFAT/NT Filesystems  --->
    	    <*> MSDOS fs support
    	    <*> VFAT (Windows-95) fs support
    	    (iso8859-1) Default iocharset for FAT
    	    <*> exFAT filesystem support
    		<*> NTFS file system support
      [*] Miscellaneous filesystems  --->
            <*> ADFS file system support
            <*> Amiga FFS file system support
    		<*> Apple Macintosh file system support
    		<*> Apple Extended HFS file system support
    		<*> BeOS file system (BeFS) support (read only)
    		<*> EFS file system support (read only)
    		<*> Minix file system support
    		<*> OS/2 HPFS file system support
    		<*> ROM file system support
    		<*> System V/Xenix/V7/Coherent file system support
    		<*> UFS file system support
    		<*> EROFS file system support
      [*] Network File Systems  --->
    	    <*> SMB3 and CIFS support (advanced network filesystem)
    		[*]   Support legacy servers which use less secure dialects
    		[*]     Support legacy servers which use weaker LANMAN security
    		[*]   CIFS extended attributes
      -*- Native language support  --->
            <*> Codepage 437 (United States, Canada)
    		<*> ASCII (United States)
    		<*> NLS ISO 8859-1  (Latin 1; Western European Languages)
    		-*- NLS UTF-8

    Kernel hacking  --->
          Generic Kernel Debugging Instruments  --->
            [*] Debug Filesystem
\`\`\`

## Windows/Amiga
Some windows and amiga files are not included due to being commercial software that is still available. This includes the HD images used by the QEMU layer. Sorry.

## Programs
Package | Program | Overlay
------- | ------- | -------
${programs.multiSort([p => p.meta.gentooPackage, p => p.bin()]).map(p => (`${p.meta.gentooPackage} | [${p.bin()}](${p.meta.website}) | ${(p.meta.gentooOverlay || "")}`)).join("\n")}

## Gentoo
Gentoo users can more easily install all the above by adding the [dexvert overlay](https://github.com/Sembiance/dexvert-gentoo-overlay).

For proper CUDA support, you'll want to look up your [NVIDIA card here](https://developer.nvidia.com/cuda-gpus#compute)
Then add to your /etc/portage/make.conf these 2 lines:
TF_CUDA_COMPUTE_CAPABILITIES=7.0
USE="$USE cuda"

Certain Gentoo USE flags may also be required for proper feature support.

You should be able to install everything you need on Gentoo with this one command:

\`\`\`
USE="${programs.flatMap(p => (p.meta.gentooUseFlags || "").split(" ")).filterEmpty().multiSort(v => v).unique().join(" ")}" emerge ${programs.map(p => p.meta.gentooPackage).multiSort(v => v).unique().join(" ")}
\`\`\``, XU.UTF8, this);
	},
	XU.FINISH
);
