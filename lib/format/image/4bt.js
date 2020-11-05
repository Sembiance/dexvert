"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "GoDot 4Bit Image",
	website  : "http://fileformats.archiveteam.org/wiki/GoDot",
	ext      : [".4bt"],
	magic    : ["GoDot 4-bit graphics bitmap"]
};

exports.converterPriorty = ["recoil2png", "nconvert"];
