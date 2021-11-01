"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Haiku Vector Icon Format",
	website  : "http://fileformats.archiveteam.org/wiki/Haiku_Vector_Icon_Format",
	ext      : [".hvif"],
	mimeType : "image/x-hvif",
	magic    : ["Haiku Vector Icon Format"]
};

exports.converterPriority = ["abydosconvert"];
