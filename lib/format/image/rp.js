"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Rainbow Painter",
	website  : "http://fileformats.archiveteam.org/wiki/Rainbow_Painter",
	ext      : [".rp"],
	fileSize : 10242
};

exports.converterPriorty = ["recoil2png", "nconvert", "view64"];
