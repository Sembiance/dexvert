"use strict";
/* eslint-disable max-len */
const XU = require("@sembiance/xu"),
	fileUtil = require("@sembiance/xutil").file,
	runUtil = require("@sembiance/xutil").run,
	path = require("path"),
	fs = require("fs"),
	tiptoe = require("tiptoe");

tiptoe(
	function findPrograms()
	{
		fileUtil.glob(path.join(__dirname, "..", "lib", "program"), "*.js", {nodir : true}, this.parallel());
		runUtil.run(path.join(__dirname, "..", "bin", "dexid"), ["--help"], runUtil.SILENT, this.parallel());
		runUtil.run(path.join(__dirname, "..", "bin", "dexvert"), ["--help"], runUtil.SILENT, this.parallel());
	},
	function generateReadme(programFilePaths, dexidUsage, dexvertUsage)
	{
		const programs = programFilePaths.map(programFilePath => require(programFilePath));	// eslint-disable-line node/global-require

		// These programs are used by virtualXRun
		programs.push({bin() { return "Xvfb"; }, meta : {gentooPackage : "x11-base/xorg-server", website : "https://www.x.org/wiki/", gentooUseFlags : "libglvnd xorg xvfb"}});
		programs.push({bin() { return "hsetroot"; }, meta : {gentooPackage : "x11-misc/hsetroot", website : "https://wiki.gentoo.org/wiki/No_homepage"}});
		programs.push({bin() { return "ffmpeg"; }, meta : {gentooPackage : "media-video/ffmpeg", website : "https://ffmpeg.org/", gentooUseFlags : "X alsa amr bzip2 encode fontconfig gpl iconv jpeg2k lzma mp3 network opengl openssl opus postproc svg theora threads truetype v4l vaapi vdpau vorbis vpx webp x264 xvid zlib"}});

		// Some programs are nodejs scripts that call multiple gentoo packages and binaries (such as uniso)
		const multiProgs = programs.filter(p => Array.isArray(p.meta.gentooPackage));
		programs.filterInPlace(p => !Array.isArray(p.meta.gentooPackage));

		multiProgs.forEach(multiProg => programs.push(...multiProg.meta.gentooPackage.map((subGentooPackage, i) => ({ bin() { return multiProg.meta.bin[i]; }, meta : {gentooPackage : subGentooPackage, website : multiProg.meta.website[i] || ""} }))));

		fs.writeFile(path.join(__dirname, "..", "README.md"), `# dexvert - Decompress EXtract conVERT

This is a nodejs based program that can decompress, extract and convert a wide variety of old file formats to modern day equilivants.

## Install
dexvert requires a LOT of programs and some kernel options to be set. See Requirements below. Once satisified, install with:
\`npm install dexvert -g\`

## Usage
\`\`\`
${dexvertUsage}
\`\`\`

\`\`\`
${dexidUsage}
\`\`\`

Use as a nodejs module:

\`\`\`javascript
const dexvert = require("dexvert");

dexvert.process(inputFilePath, outputDirPath, options, cb);
dexvert.identify(inputFilePath, cb);
\`\`\`

# Requirements

## Kernel
WIP

## Programs
Gentoo users can simply install the packages below, some are available in my Gentoo [dexvert overlay](https://github.com/Sembiance/dexvert-gentoo-overlay). Certain Gentoo USE flags may also be require, see further below. Other operating systems have not been tested at all. A docker container could be possible, but there would still need to be certain kernel options set for proper functioning.

Package | Program | Overlay
------- | ------- | -------
${programs.multiSort([p => p.meta.gentooPackage, p => p.bin()]).map(p => (`${p.meta.gentooPackage} | [${p.bin()}](${p.meta.website}) | ${(p.meta.gentooOverlay || "")}`)).join("\n")}

Gentoo users can install all the above with this single command:
\`\`\`
USE="${programs.flatMap(p => (p.meta.gentooUseFlags || "").split(" ")).filterEmpty().multiSort(v => v).unique().join(" ")}" emerge ${programs.map(p => p.meta.gentooPackage).multiSort(v => v).unique().join(" ")}
\`\`\`
		`, XU.UTF8, this);
	},
	XU.FINISH
);
