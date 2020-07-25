"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Truevision Targa Graphic",
	website  : "http://fileformats.archiveteam.org/wiki/TGA",
	ext      : [".tga", ".targa", ".tpic", ".icb", ".vda", ".vst"],
	mimeType : "image/x-tga",
	magic    : ["Truevision TGA", "Targa image data"]
};

exports.converterPriorty = ["convert"];
