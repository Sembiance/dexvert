"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Dali",
	website  : "http://fileformats.archiveteam.org/wiki/Dali",
	ext      : [".sd0", ".sd1", ".sd2", ".hpk", ".lpk", ".mpk"],
	fileSize : {".sd0,.sd1,.sd2" : 32128}
};

exports.converterPriority = ["recoil2png", "nconvert"];
