"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name      : "Portfolio Graphics Compressed",
	website   : "http://fileformats.archiveteam.org/wiki/PGC_(Portfolio_Graphics_Compressed)",
	ext       : [".pgc"],
	magic     : ["PGC Portfolio Graphics Compressed bitmap"]
};

exports.converterPriority = ["recoil2png", "nconvert"];
