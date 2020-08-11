"use strict";
const XU = require("@sembiance/xu");
exports.meta =
{
	name    : "Tiny Stuff",
	website : "http://fileformats.archiveteam.org/wiki/Tiny_Stuff",
	ext     : [".tn1", ".tn2", ".tn3", ".tn4", ".tny"],
	magic   : ["Tiny Stuff format bitmap"]
};

exports.converterPriorty = ["recoil2png", "nconvert"];
