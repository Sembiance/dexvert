"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name                : "Sinbad Slideshow",
	website             : "http://fileformats.archiveteam.org/wiki/Sinbad_Slideshow",
	ext                 : [".ssb"],
	fileSize            : 32768,
	forbidFileSizeMatch : true

};

exports.converterPriority = ["recoil2png"];
