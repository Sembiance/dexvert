"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Naïve Image Format NIA",
	website  : "http://fileformats.archiveteam.org/wiki/Na%C3%AFve_Image_Formats",
	ext      : [".nia"],
	mimeType : "image/nia",
	magic    : ["Naive Image format NIA animated bitmaps"]
};

exports.converterPriority = ["abydosconvert"];
