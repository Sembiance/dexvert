"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name       : "Zoner Zebra",
	website    : "http://fileformats.archiveteam.org/wiki/ZBR_(Zoner_Zebra)",
	ext        : [".zbr"],
	magic      : ["Zebra metafile"],
	notes      : "recConverter is the only program I know of that can convert to SVG but it fails to do so with QEMU WinXP 32bit (used to work in wine). So for now, we just convert to PNG.",
	trustMagic : true
};

exports.converterPriorty = ["nconvert", "deark"];
