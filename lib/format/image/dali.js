"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Dali",
	website  : "http://fileformats.archiveteam.org/wiki/Dali",
	ext      : [".sd0", ".sd1", ".sd2", ".hpk", ".lpk", ".mpk"],
	filesize : {".sd0,.sd1,.sd2" : 32128}
};

exports.converterPriorty = ["recoil2png", "nconvert"];
