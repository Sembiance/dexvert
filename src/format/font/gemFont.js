"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "GEM Bitmap Font",
	website : "http://fileformats.archiveteam.org/wiki/GEM_bitmap_font",
	ext     : [".gft", ".fnt"],
	magic   : ["GEM GDOS font"]
};

exports.steps = [() => ({program : "deark"})];
