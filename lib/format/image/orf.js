"use strict";
const XU = require("@sembiance/xu");
exports.meta =
{
	name     : "Olympus RAW",
	website  : "http://fileformats.archiveteam.org/wiki/ORF",
	ext      : [".orf"],
	magic    : ["Olympus RAW", "Olympus ORF raw image data", "Olympus digital camera RAW image"]
};

exports.converterPriorty = ["nconvert"];
