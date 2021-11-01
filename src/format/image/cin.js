"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Kodak Cineon",
	website  : "http://fileformats.archiveteam.org/wiki/Cineon",
	ext      : [".cin"],
	mimeType : "image/x-cineon",
	magic    : ["Kodak Cineon bitmap", "Cineon image data"]
};

exports.converterPriority = ["nconvert", "abydosconvert"];
