"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Flexible Image Transport System",
	website  : "http://fileformats.archiveteam.org/wiki/Flexible_Image_Transport_System",
	ext      : [".fit", ".fits", ".fts", ".fz"],
	mimeType : "image/fits",
	magic    : ["Flexible Image Transport System", "FITS image data"]
};

exports.converterPriorty = ["nconvert"];
