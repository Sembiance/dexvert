"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "PASTI Disk Image",
	website : "http://fileformats.archiveteam.org/wiki/STX",
	ext     : [".stx"],
	magic   : ["PASTI disk image"]
};

// Alternative extractor: https://github.com/DrCoolzic/AIR
exports.converterPriority = ["deark"];
