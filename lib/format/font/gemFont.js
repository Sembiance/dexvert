"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "GEM Bitmap Font",
	website     : "http://fileformats.archiveteam.org/wiki/GEM_bitmap_font",
	ext         : [".gft", ".fnt"],
	magic       : ["GEM GDOS font"],
	unsupported : true,
	notes       : "Bitmap font file used by programs like Neopaint for MSDOS and maybe GEM OS. Fontforge doesn't handle it"
};
