"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "PC Paint Image",
	website  : "http://fileformats.archiveteam.org/wiki/PCPaint_PIC",
	ext      : [".pic", ".clp"],
	magic    : ["PC Paint/Pictor bitmap", "PC Paint Bitmap"]
};

// deark is the only thing that appears to handle .clp files
// nconvert sometimes fails to convert, but sometimes succeeds. same command. weird.
exports.converterPriorty = ["deark", "nconvert"];
