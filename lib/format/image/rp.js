"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Rainbow Painter",
	website  : "http://fileformats.archiveteam.org/wiki/Rainbow_Painter",
	ext      : [".rp"],
	filesize : [10242]
};

exports.converterPriorty = ["recoil2png", "nconvert"];
