"use strict";
const XU = require("@sembiance/xu");
exports.meta =
{
	name     : "Pentax RAW",
	website  : "http://fileformats.archiveteam.org/wiki/Pentax_PEF",
	ext      : [".pef", ".ptx"],
	magic    : ["Pentax RAW image"]
};

exports.converterPriorty = ["nconvert"];
