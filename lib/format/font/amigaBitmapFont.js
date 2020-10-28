"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Amiga Bitmap Font",
	website : "http://fileformats.archiveteam.org/wiki/Amiga_bitmap_font",
	ext     : [".font"],
	magic   : ["Amiga bitmap Font", "AmigaOS bitmap font"],
	notes   : "Fony (Win32/wine) (see sandbox/app/) is supposed to be able to open these, but I wasn't able to use it"
};

exports.steps = [() => ({program : "Fony"})];

