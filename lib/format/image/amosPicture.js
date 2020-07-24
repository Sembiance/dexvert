"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "AMOS Picture Bank",
	website  : "http://fileformats.archiveteam.org/wiki/AMOS_Picture_Bank",
	ext      : [".abk"],
	magic    : ["AMOS Picture Bank"]
};

exports.converterPriorty = ["deark"];
