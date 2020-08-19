"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "EggPaint",
	website : "http://fileformats.archiveteam.org/wiki/EggPaint",
	ext     : [".trp"],
	magic   : ["EggPaint bitmap", "True Colour Picture bitmap"],
	notes   : "Also known as the 'True Colour Picture' format"
};

exports.converterPriorty = ["recoil2png"];
