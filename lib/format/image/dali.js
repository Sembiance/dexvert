"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Dali",
	website  : "http://fileformats.archiveteam.org/wiki/Dali",
	ext      : [".sd0", ".sd1", ".sd2"],
	filesize : [32128]
};

exports.converterPriorty = ["recoil2png", "nconvert"];
