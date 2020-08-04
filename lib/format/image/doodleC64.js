"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Doodle C64",
	website  : "http://fileformats.archiveteam.org/wiki/Doodle!_(C64)",
	ext      : [".dd", ".jj"],
	filesize : [9218, 9026, 9346]
};

exports.converterPriorty = ["recoil2png", "nconvert"];
