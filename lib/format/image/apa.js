"use strict";
const XU = require("@sembiance/xu");
exports.meta =
{
	name     : "Atari AP* Image",
	website  : "http://fileformats.archiveteam.org/wiki/AP*",
	ext      : [".256", ".ap2", ".apa", ".apc", ".plm"],
	filesize : [7720, 7680]
};

exports.converterPriorty = ["recoil2png"];
