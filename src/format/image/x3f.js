"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Sigma/Foveon X3F",
	website  : "http://fileformats.archiveteam.org/wiki/X3F",
	ext      : [".x3f"],
	magic    : ["Sigma RAW Image", "Foveon X3F raw image data", "Sigma - Foveon X3 raw picture"],
	mimeType : "image/x-sigma-x3f"
};

exports.converterPriorty = ["dcraw", "convert", "abydosconvert", "nconvert"];
