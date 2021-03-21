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
		fileUtil.glob(path.join(__dirname, "..", "lib", "program"), "**/*.js", {nodir : true}, this);
	},
	function generateReadme(programFilePaths)
	{
		const programs = programFilePaths.map(programFilePath => require(programFilePath));

		// bin/runServers.js
		programs.push({bin() { return "jq"; }, meta : {gentooPackage : "app-misc/jq", website : "https://stedolan.github.io/jq/"}});

		// hashUtil.hash
		programs.push({bin() { return "b3sum"; }, meta : {gentooPackage : "app-crypt/blake3", website : "hhttps://github.com/BLAKE3-team/BLAKE3"}});

		// runUtil.run
		programs.push({bin() { return "Xvfb"; }, meta : {gentooPackage : "x11-base/xorg-server", website : "https://www.x.org/wiki/", gentooUseFlags : "libglvnd xorg xvfb"}});
		programs.push({bin() { return "hsetroot"; }, meta : {gentooPackage : "x11-misc/hsetroot", website : "https://wiki.gentoo.org/wiki/No_homepage"}});

		// videoUtil.info (and DOS video recording too)
		programs.push({bin() { return "mplayer"; }, meta : {gentooPackage : "media-video/mplayer", website : "http://www.mplayerhq.hu/", gentooUseFlags : "X a52 alsa cdio dga dts dv dvd dvdnav enca encode iconv joystick jpeg libass live lzo mad mng mp3 network opengl osdmenu png rtc shm tga theora truetype unicode v4l vcd vdpau vorbis x264 xinerama xscreensaver xv xvid"}});
		
		// unicodeUtils.fixDirEncodings
		programs.push({bin() { return "convmv"; }, meta : {gentooPackage : "app-text/convmv", website : "https://www.j3e.de/linux/convmv/"}});

		// lib/util/wine.js
		programs.push({bin() { return "wine"; }, meta : {gentooPackage : "app-emulation/wine-vanilla", website : "https://www.winehq.org/"}});

		// dosUtil
		programs.push({bin() { return "dosbox"; }, meta : {gentooPackage : "games-emulation/dosbox", website : "http://dosbox.sourceforge.net/", gentooUseFlags : "alsa opengl"}});
		programs.push({bin() { return "xdotool"; }, meta : {gentooPackage : "x11-misc/xdotool", website : "https://www.semicomplete.com/projects/xdotool/"}});

		// python tensorflow server
		programs.push({bin() { return ""; }, meta : {gentooPackage : "sci-libs/tensorflow", website : "https://www.tensorflow.org/"}});
		programs.push({bin() { return ""; }, meta : {gentooPackage : "dev-python/flask", website : "https://github.com/pallets/flask/"}});
		programs.push({bin() { return ""; }, meta : {gentooPackage : "dev-python/pillow", website : "https://python-pillow.org/"}});

		programs.filterInPlace(p => p.meta.hasOwnProperty("gentooPackage"));

		// Some programs are nodejs scripts that call multiple gentoo packages and binaries (such as uniso)
		const multiProgs = programs.filter(p => Array.isArray(p.meta.gentooPackage));
		programs.filterInPlace(p => !Array.isArray(p.meta.gentooPackage));

		multiProgs.forEach(multiProg => programs.push(...multiProg.meta.gentooPackage.map((subGentooPackage, i) => ({ bin() { return multiProg.meta.bin[i]; }, meta : {kernel : multiProg.meta.kernel || undefined, gentooPackage : subGentooPackage, website : multiProg.meta.website[i] || ""} }))));

		fs.writeFile(path.join(__dirname, "..", "INSTALL.md"), `# Install
\`npm install dexvert -g\`
		
# Requirements

## Kernel
\`\`\`
File systems  --->
	  Processor type and features --->
	    [*] NUMA Memory Allocation and Scheduler Support
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
  [*] Miscellaneous filesystems  --->
        <*> Amiga FFS file system support
		<*> Apple Macintosh file system support
		<*> Apple Extended HFS file system support
  -*- Native language support  --->
        <*> Codepage 437 (United States, Canada)
		<*> ASCII (United States)
		<*> NLS ISO 8859-1  (Latin 1; Western European Languages)
		-*- NLS UTF-8
\`\`\`

## Wine/Amiga
Some win32 wine programs and amiga files are not included due to being commercial software that is still available.

## Programs
Gentoo users can simply install the packages below, some are available in my Gentoo [dexvert overlay](https://github.com/Sembiance/dexvert-gentoo-overlay). Certain Gentoo USE flags may also be require, see further below. Other operating systems have not been tested at all. A docker container could be possible, but there would still need to be certain kernel options set for proper functioning.

Package | Program | Overlay
------- | ------- | -------
${programs.multiSort([p => p.meta.gentooPackage, p => p.bin()]).map(p => (`${p.meta.gentooPackage} | [${p.bin()}](${p.meta.website}) | ${(p.meta.gentooOverlay || "")}`)).join("\n")}

Gentoo users can install all the above required programs with this single command:
\`\`\`
USE="${programs.flatMap(p => (p.meta.gentooUseFlags || "").split(" ")).filterEmpty().multiSort(v => v).unique().join(" ")}" emerge ${programs.map(p => p.meta.gentooPackage).multiSort(v => v).unique().join(" ")}
\`\`\``, XU.UTF8, this);
	},
	XU.FINISH
);
