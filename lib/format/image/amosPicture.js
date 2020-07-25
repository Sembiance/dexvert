"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "AMOS Picture Bank",
	website  : "http://fleformats.archiveteam.org/wiki/AMOS_Picture_Bank",
	ext      : [".abk"],
	mimeType : "application/x-amos-memorybank",
	magic    : ["AMOS Picture Bank"]
};

exports.converterPriorty = ["deark", "abydosconvert"];
