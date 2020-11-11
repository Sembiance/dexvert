"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name                : "Mad Designer",
	website             : "http://fileformats.archiveteam.org/wiki/Mad_Designer",
	ext                 : [".mbg"],
	fileSize            : 16384,
	forbidFileSizeMatch : true // recoil2png will convert any file, so we should only do it if we also have the proper extension
};

exports.converterPriorty = ["recoil2png"];
