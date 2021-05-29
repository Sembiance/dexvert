"use strict";
const XU = require("@sembiance/xu"),
	C = require("../../C.js");

exports.meta =
{
	name        : "Draw 256 Image",
	website     : "http://fileformats.archiveteam.org/wiki/Draw256",
	ext         : [".vga"],
	unsafe      : true,
	priority    : C.PRIORITY.VERYLOW,
	unsupported : true,
	notes       : "Sadly Draw256 for DOS takes any file ending with .VGA and renders garbage. Cannot determine before if it's a proper file. Due to common extension and extreme rarity of Draw256 files in the wild, this format is marked unsupported."
};

//exports.converterPriorty = ["draw256"];
