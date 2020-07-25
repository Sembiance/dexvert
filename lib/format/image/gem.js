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

exports.converterPriorty = ["abydosconvert", "deark", "nconvert"];
