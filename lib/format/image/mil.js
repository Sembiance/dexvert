"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Micro Illustrator",
	website  : "http://fileformats.archiveteam.org/wiki/Micro_Illustrator",
	ext      : [".mil"],
	fileSize : 10022
};

exports.converterPriorty = ["recoil2png", "nconvert"];
