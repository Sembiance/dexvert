"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name                : "Face Painter",
	website             : "http://fileformats.archiveteam.org/wiki/Face_Painter",
	ext                 : [".fcp", ".fpt"],
	mimeType            : "image/x-face-painter",
	fileSize            : 10004,
	forbidFileSizeMatch : true
};

exports.converterPriority = ["recoil2png", "abydosconvert", "view64"];
