"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "GEM Raster Bitmap",
	website  : "http://fileformats.archiveteam.org/wiki/GEM_Raster",
	ext      : [".img", ".ximg"],
	mimeType : "image/x-gem",
	magic    : ["GEM bitmap", "GEM HYPERPAINT Image data", "GEM Image data"]
};

// Abydos and nconvert are the only 2 that handle the color in flag_b24 and tru256
// Sadly though, nconvert messes up some other images colorspaces
exports.converterPriorty = ["abydosconvert", "deark", "nconvert"];
