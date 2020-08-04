"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Paintworks",
	website  : "http://fileformats.archiveteam.org/wiki/Paintworks",
	ext      : [".cl0", ".sc0", ".cl1", ".sc1", ".cl2", ".sc2"]
};

exports.converterPriorty = ["recoil2png", "nconvert"];
