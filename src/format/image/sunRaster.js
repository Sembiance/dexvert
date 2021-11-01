"use strict";
/* eslint-disable node/global-require */
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Sun Raster Bitmap",
	website        : "http://fileformats.archiveteam.org/wiki/Sun_Raster",
	ext            : [".ras", ".rast", ".rs", ".scr", ".sr", ".sun", ".im1", ".im8", ".im24", ".im32"],
	mimeType       : "image/x-sun-raster",
	magic          : ["Sun Raster bitmap", /^Sun [Rr]aster [Ii]mage/],
	forbiddenMagic : require("../executable/windowsSCR.js").meta.magic	// Never want to convert windows SCR files as an image
};

// abydosconvert also supports this format, but it hangs in an infinite loop when passing it an invalid image, so we don't bother including it below
exports.converterPriority = ["deark", "nconvert"];
