"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name                : "Champions' Interlace Image",
	website             : "http://fileformats.archiveteam.org/wiki/Champions%27_Interlace",
	ext                 : [".cci", ".cin"],
	fileSize            : {".cin" : [15360, 16004, 16384]},
	forbidFileSizeMatch : true
};

exports.converterPriority = ["recoil2png"];
