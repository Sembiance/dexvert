"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "Anex86 PC98 Floppy Image",
	website     : "http://fileformats.archiveteam.org/wiki/Anex86_PC98_floppy_image",
	ext         : [".fdi"],
	magic       : ["Anex86 PC98 floppy image"],
	unsupported : true,
	notes       : XU.trim`
		The DiskExplorer/editdisk program is supposed to read these, but it fails on my sample files. 
		Removing the 4k header and attempting to mount the raw image fails. Likely because of a disk format unique to PC98.
		I was able to extract the files by creating a HDD image with anex86 and formatting it by following: http://www.retroprograms.com/mirrors/Protocatbert/protocat.htm
		After that I could run anex86 with dos6.2 in FDD #1 and the FDI image in FDD #2. Then hit Escape and at the DOS prompt I could COPY B:\* C:
		Then I exited anex86 and then I was able to use wine editdisk.exe to open the HDD image, ctrl-a all the files and ctrl-e extract them.
		So I could automate this and support FDI extraction. But right now I just don't see the value in doing so.`
};

