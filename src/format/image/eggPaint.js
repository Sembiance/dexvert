"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "EggPaint / True Colour Picture",
	website : "http://fileformats.archiveteam.org/wiki/EggPaint",
	ext     : [".trp"],
	magic   : ["EggPaint bitmap", "True Colour Picture bitmap"]
};

exports.converterPriority = ["recoil2png"];
