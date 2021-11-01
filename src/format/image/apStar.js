"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name                : "Atari AP* Image",
	website             : "http://fileformats.archiveteam.org/wiki/AP*",
	ext                 : [".256", ".ap2", ".apa", ".apc", ".plm", ".mic"],
	fileSize            : [7720, 7680, 7684],
	forbidFileSizeMatch : true
};

exports.converterPriority = ["recoil2png"];
