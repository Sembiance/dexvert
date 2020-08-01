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

exports.converterPriorty = ["nconvert", "convert"];
