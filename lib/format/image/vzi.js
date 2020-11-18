"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name                : "VertiZontal Interlacing",
	website             : "http://fileformats.archiveteam.org/wiki/VertiZontal_Interlacing",
	ext                 : [".vzi"],
	fileSize            : 16000,
	forbidFileSizeMatch : true	// recoil2png will convert any file, so we should only do it if we also have the proper extension
};

exports.converterPriorty = ["recoil2png"];
