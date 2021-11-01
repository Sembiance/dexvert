"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Free Lossless Image Format",
	website  : "http://fileformats.archiveteam.org/wiki/FLIF",
	ext      : [".flif"],
	mimeType : "image/x-flif",
	magic    : ["Free Lossless Image Format", "FLIF"]
};

exports.converterPriority = ["abydosconvert"];
