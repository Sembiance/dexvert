"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "ImageLab Image",
	website  : "http://fileformats.archiveteam.org/wiki/ImageLab/PrintTechnic",
	ext      : [".b_w", ".b&w"],
	mimeType : "image/x-imagelab",
	magic    : ["ImageLab bitmap"]
};

exports.converterPriority = ["nconvert", "abydosconvert"];
