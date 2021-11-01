"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name                : "Atari MCS",
	website             : "http://fileformats.archiveteam.org/wiki/MCS",
	ext                 : [".mcs"],
	fileSize            : 10185,
	forbidFileSizeMatch : true
};

exports.converterPriority = ["recoil2png"];
