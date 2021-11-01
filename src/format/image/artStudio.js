"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name                : "Art Studio",
	website             : "http://fileformats.archiveteam.org/wiki/Art_Studio",
	ext                 : [".art", ".aas"],
	magic               : ["C64 Hires bitmap"],
	weakMagic           : true,
	fileSize            : [].pushSequence(9000, 9010),
	forbidFileSizeMatch : true
};

exports.converterPriority = ["recoil2png", "view64"];
