"use strict";
const XU = require("@sembiance/xu");
exports.meta =
{
	name    : "X Window Dump",
	website : "http://fileformats.archiveteam.org/wiki/XWD",
	ext     : [".xwd", ".dmp"],
	safeExt() { return ".xwd"; },
	magic   : ["X-Windows Screen Dump", "XWD X Windows Dump image data"]
};

// Neither nconvert nor convert properly handle all the files, but nconvert does a little bit better with color images
exports.converterPriorty = ["nconvert", "convert"];
