"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Lempel-Ziv Archive",
	website : "http://fileformats.archiveteam.org/wiki/LZX",
	ext     : [".lzx"],
	magic   : ["LZX compressed archive", "LZX Amiga compressed archive"]
};

exports.steps = [() => ({program : "unar"})];
