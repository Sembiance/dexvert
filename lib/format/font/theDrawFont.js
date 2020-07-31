"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "The Draw Font",
	website     : "http://fileformats.archiveteam.org/wiki/TheDraw_font",
	ext         : [".tdf"],
	magic       : ["TheDraw Fonts"],
	unsupported : true,
	notes       : "Bitmap font file used by programs like Neopaint for MSDOS and maybe GEM OS. Fontforge doesn't handle it"
};
