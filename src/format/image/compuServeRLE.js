"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "CompuServe RLE",
	website : "http://fileformats.archiveteam.org/wiki/CompuServe_RLE",
	ext     : [".rle"],
	magic   : ["CompuServe RLE bitmap"],
	notes   : "RRCP1.RLE isn't able to be converted by recoil2png and cistopbm handles it better, but still a bit corrupted."
};

exports.converterPriorty = ["recoil2png", "cistopbm"];
