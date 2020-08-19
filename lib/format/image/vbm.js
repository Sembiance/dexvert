"use strict";
const XU = require("@sembiance/xu");
exports.meta =
{
	name    : "VDC BitMap",
	website : "http://fileformats.archiveteam.org/wiki/VBM_(VDC_BitMap)",
	ext     : [".vbm", ".bm"],
	magic   : ["VDC BitMap"]
};

exports.converterPriorty = ["recoil2png"];
