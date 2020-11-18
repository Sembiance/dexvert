"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "Amiga Bitmap Font",
	website     : "http://fileformats.archiveteam.org/wiki/Amiga_bitmap_font",
	ext         : [".font"],
	magic       : ["Amiga bitmap Font", "AmigaOS bitmap font"]
};

exports.steps = [() => ({program : "Fony"})];

