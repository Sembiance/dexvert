"use strict";
const XU = require("@sembiance/xu");
exports.meta =
{
	name     : "Fujifilm RAW",
	website  : "http://fileformats.archiveteam.org/wiki/RAF",
	ext      : [".raf"],
	magic    : ["Fujifilm Raw image"]
};

exports.converterPriorty = ["nconvert"];
