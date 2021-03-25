"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Cheese",
	website  : "http://fileformats.archiveteam.org/wiki/Cheese",
	ext      : [".che"],
	mimeType : "image/x-cheese",
	fileSize : 20482
};

exports.converterPriorty = ["recoil2png", "nconvert", "abydosconvert", "view64"];
