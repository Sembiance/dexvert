"use strict";
const XU = require("@sembiance/xu");
exports.meta =
{
	name     : "Nikon Electronic Format",
	website  : "http://fileformats.archiveteam.org/wiki/Nikon",
	ext      : [".nef", ".nrw"],
	magic    : ["Nikon Digital SLR Camera Raw Image File", "Nikon raw image"],
	mimeType : "image/x-nikon-nef"
};

exports.converterPriorty = ["convert", "abydosconvert", "nconvert"];
