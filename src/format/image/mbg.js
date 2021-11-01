"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name                : "Mad Designer",
	website             : "http://fileformats.archiveteam.org/wiki/Mad_Designer",
	ext                 : [".mbg"],
	fileSize            : 16384,
	forbidFileSizeMatch : true
};

exports.converterPriority = ["recoil2png"];
