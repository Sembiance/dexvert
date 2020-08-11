"use strict";
const XU = require("@sembiance/xu");
exports.meta =
{
	name    : "Award BIOS Logo",
	website : "http://fileformats.archiveteam.org/wiki/Award_BIOS_logo",
	ext     : [".epa"],
	magic   : [/^Award BIOS [Ll]ogo/]
};

// nconvert, as usual, messes up several files
exports.converterPriorty = ["recoil2png", "deark", "nconvert"];
