"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "TRS-80 Disk Image",
	website : "http://fileformats.archiveteam.org/wiki/DMK",
	ext     : [".dmk", ".dsk"],
	magic   : ["TRS-80 DMK"]
};

exports.converterPriority = ["trsread"];
