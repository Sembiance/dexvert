"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Canon Image File Format",
	website  : "http://fileformats.archiveteam.org/wiki/Camera_Image_File_Format",
	ext      : [".crw"],
	magic    : ["Canon CIFF raw image data", "Canon RAW format"],
	mimeType : "image/x-canon-crw"
};

exports.converterPriorty = ["convert", "abydosconvert", "nconvert"];
