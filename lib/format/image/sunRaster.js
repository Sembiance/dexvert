"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Sun Raster Bitmap",
	website  : "http://fileformats.archiveteam.org/wiki/Sun_Raster",
	ext      : [".ras", ".rast", ".rs", ".scr", ".sr", ".sun", ".im1", ".im8", ".im24", ".im32"],
	mimeType : "image/x-sun-raster",
	magic    : ["Sun Raster bitmap", /^Sun [Rr]aster [Ii]mage/]
};

exports.converterPriorty = ["deark", "abydosconvert", "nconvert"];
