"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name                : "ZX Spectrum - Tricolor RGB",
	website             : "http://fileformats.archiveteam.org/wiki/Tricolor_RGB",
	ext                 : [".3"],
	mimeType            : "image/x-tricolor-rgb",
	fileSize            : 18432,
	forbidFileSizeMatch : true
};

exports.converterPriority = ["recoil2png", "abydosconvert"];
