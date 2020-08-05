"use strict";
const XU = require("@sembiance/xu");
exports.meta =
{
	name     : "Digital Negative",
	website  : "http://fileformats.archiveteam.org/wiki/DNG",
	ext      : [".dng"],
	magic    : ["Digital Negative Format"]
};

exports.converterPriorty = ["nconvert"];
