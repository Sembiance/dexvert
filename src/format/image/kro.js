"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Kolor Raw",
	website  : "http://fileformats.archiveteam.org/wiki/Kolor_Raw",
	ext      : [".kro"],
	magic    : ["Kolor Raw image format"]
};

exports.converterPriority = ["nconvert"];
