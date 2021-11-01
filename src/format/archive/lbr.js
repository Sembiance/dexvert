"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "LBR Archive",
	website : "http://fileformats.archiveteam.org/wiki/LBR",
	ext     : [".lbr"],
	magic   : ["LBR archive data", "LU library"]
};

exports.converterPriority = ["lbrate"];
