"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name                : "Art Director",
	website             : "http://fileformats.archiveteam.org/wiki/Art_Director",
	ext                 : [".art"],
	fileSize            : 32512,
	forbidFileSizeMatch : true
};

exports.converterPriority = ["recoil2png"];
