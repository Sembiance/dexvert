"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Naïve Image Format NIE",
	website  : "http://fileformats.archiveteam.org/wiki/Na%C3%AFve_Image_Formats",
	ext      : [".nie"],
	mimeType : "image/nie",
	magic    : ["Naive Image format NIE bitmap"]
};

exports.converterPriority = ["abydosconvert"];
