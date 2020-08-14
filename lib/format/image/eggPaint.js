"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "EggPaint",
	website : "http://fileformats.archiveteam.org/wiki/EggPaint",
	ext     : [".trp"],
	magic   : ["EggPaint bitmap"]
};

exports.converterPriorty = ["recoil2png"];
