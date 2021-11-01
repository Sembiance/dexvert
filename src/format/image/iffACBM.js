"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "IFF Amiga Contiguous Bitmap",
	website  : "http://fileformats.archiveteam.org/wiki/ILBM#ACBM",
	ext      : [".lbm", ".ilbm", ".iff", ".acbm"],
	magic    : ["IFF data, ACBM continuous image", "IFF Amiga Contiguous BitMap"]
};

exports.converterPriority = ["recoil2png"];
