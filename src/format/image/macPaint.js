"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "MacPaint Image",
	website : "http://fileformats.archiveteam.org/wiki/MacPaint",
	ext     : [".mac", ".pntg", ".pic"],
	magic   : ["MacPaint image data"]
};

// deark correctly identifies the original filename from meta info within the file itself
exports.converterPriorty = ["deark"];
