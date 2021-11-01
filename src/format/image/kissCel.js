"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Kisekae Set System Cell",
	website  : "http://fileformats.archiveteam.org/wiki/KiSS_CEL",
	ext      : [".cel", ".kcf"],
	mimeType : "image/x-kiss-cel",
	magic    : ["KiSS CEL bitmap"]
};

exports.converterPriority = ["recoil2png", "nconvert", "abydosconvert"];
