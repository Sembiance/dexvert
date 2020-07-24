"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "PC Paint Image",
	website  : "http://fileformats.archiveteam.org/wiki/PCPaint_PIC",
	ext      : [".pic", ".clp"],
	magic    : ["PC Paint/Pictor bitmap", "PC Paint Bitmap"]
};

exports.converterPriorty = ["nconvert"];
