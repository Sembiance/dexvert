"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Face Painter",
	website  : "http://fileformats.archiveteam.org/wiki/Face_Painter",
	ext      : [".fcp", ".fpt"],
	mimeType : "image/x-face-painter",
	fileSize : 10004
};

exports.converterPriorty = ["abydosconvert", "recoil2png", "view64"];
