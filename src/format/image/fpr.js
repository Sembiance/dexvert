"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "FLI Profi",
	website     : "http://fileformats.archiveteam.org/wiki/FLI_Profi",
	ext         : [".fpr", ".flp"],
	unsupported : true,
	notes       : "Due to no known magic yet and how recoil2png/view64 will convert ANYTHING, we disable this for now."
};

//exports.converterPriority = ["recoil2png", "view64"];
