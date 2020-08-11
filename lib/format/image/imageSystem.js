"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Image System",
	website  : "http://fileformats.archiveteam.org/wiki/Image_System",
	ext      : [".ish", ".ism"]
};

// recoil2png doesn't properly handle some files, nconvert does a better job here
exports.converterPriorty = ["nconvert", "recoil2png"];
