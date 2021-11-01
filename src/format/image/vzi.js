"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name                : "VertiZontal Interlacing",
	website             : "http://fileformats.archiveteam.org/wiki/VertiZontal_Interlacing",
	ext                 : [".vzi"],
	fileSize            : 16000,
	forbidFileSizeMatch : true
};

exports.converterPriority = ["recoil2png"];
