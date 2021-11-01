"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name                : "XGA",
	website             : "http://fileformats.archiveteam.org/wiki/XGA_(Falcon)",
	ext                 : [".xga"],
	mimeType            : "image/x-xga",
	fileSize            : [153600, 368640],
	forbidFileSizeMatch : true
};

exports.converterPriority = ["recoil2png", "abydosconvert"];
