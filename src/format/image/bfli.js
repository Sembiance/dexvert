"use strict";
const XU = require("@sembiance/xu");
exports.meta =
{
	name     : "Big Flexible Line Interpretation",
	website  : "http://fileformats.archiveteam.org/wiki/BFLI",
	ext      : [".bfli"],
	magic    : ["Big Flexible Line Interpretation bitmap"],
	fileSize : 33795
};

exports.converterPriority = ["recoil2png"];
