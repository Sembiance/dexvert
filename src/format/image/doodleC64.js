"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Doodle C64",
	website  : "http://fileformats.archiveteam.org/wiki/Doodle!_(C64)",
	ext      : [".dd", ".jj"],
	magic    : ["Doodle bitmap (compressed)"],
	fileSize : {".dd" : [9218, 9026, 9346]}
};

exports.converterPriority = ["recoil2png", "nconvert"];
