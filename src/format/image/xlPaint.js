"use strict";
const XU = require("@sembiance/xu"),
	C = require("../../C.js");

exports.meta =
{
	name     : "XL-Paint",
	website  : "http://fileformats.archiveteam.org/wiki/XL-Paint",
	ext      : [".xlp", ".max", ".raw"],
	magic    : ["XL-Paint MAX bitmap"],
	fileSize : {".raw" : [792, 15372]},
	// When it comes to 'ext' matching .raw and .max, it's more likely this then it is the other .raw extension formats
	priority : C.PRIORITY.HIGH

};

exports.converterPriority = ["recoil2png"];
