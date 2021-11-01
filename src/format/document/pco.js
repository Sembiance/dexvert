"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "PC-Outline Document",
	website : "http://fileformats.archiveteam.org/wiki/PC-Outline",
	ext     : [".pco"],
	magic   : ["PC-Outline outline"]
};

exports.converterPriority = ["pco"];
