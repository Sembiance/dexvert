"use strict";
const XU = require("@sembiance/xu");
exports.meta =
{
	name     : "Epson RAW File",
	website  : "http://fileformats.archiveteam.org/wiki/ERF",
	ext      : [".erf"],
	magic    : ["Epson Raw Image Format"]
};

exports.converterPriorty = ["nconvert"];
