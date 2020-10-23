"use strict";
const XU = require("@sembiance/xu");
exports.meta =
{
	name     : "Minolta RAW",
	website  : "http://fileformats.archiveteam.org/wiki/Minolta",
	ext      : [".mrw"],
	magic    : ["Minolta RAW", "Minolta Dimage camera raw", "Minolta Dimage RAW image"],
	mimeType : "image/x-minolta-mrw"
};

exports.converterPriorty = ["convert", "abydosconvert", "nconvert"];
