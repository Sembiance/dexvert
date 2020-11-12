"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Nikon Electronic Format",
	website  : "http://fileformats.archiveteam.org/wiki/Nikon",
	ext      : [".nef", ".nrw"],
	magic    : ["Nikon raw image", /^TIFF image data.*manufacturer=NIKON/],
	mimeType : "image/x-nikon-nef"
};

exports.converterPriorty = ["convert", "abydosconvert", "nconvert"];
