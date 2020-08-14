"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	C = require(path.join(__dirname, "..", "..", "C.js"));

exports.meta =
{
	name     : "XL-Paint",
	website  : "http://fileformats.archiveteam.org/wiki/XL-Paint",
	ext      : [".xlp", ".max", ".raw"],
	magic    : ["XL-Paint MAX bitmap"],
	priority : C.PRIORITY.HIGH	// When it comes to 'ext' matching .raw and .max, it's more likely this then it is the other .raw extension formats

};

exports.converterPriorty = ["recoil2png"];
