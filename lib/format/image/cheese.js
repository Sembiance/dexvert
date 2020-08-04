"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Cheese",
	website  : "http://fileformats.archiveteam.org/wiki/Cheese",
	ext      : [".che"],
	mimeType : "image/x-cheese",
	filesize : [20482]
};

exports.converterPriorty = ["nconvert", "recoil2png", "abydosconvert"];
