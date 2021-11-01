"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name                : "Paradox",
	website             : "http://fileformats.archiveteam.org/wiki/Paradox",
	ext                 : [".mcpp"],
	fileSize            : 8008,
	forbidFileSizeMatch : true
};

exports.converterPriority = ["recoil2png"];
