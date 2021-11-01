"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Pro-Pack - Rob Northern Compression",
	website : "http://fileformats.archiveteam.org/wiki/RNC",
	ext     : [".rnc"],
	magic   : ["Rob Northen Compression", "PRO-PACK archive data"]
};

exports.converterPriority = ["ancient"];
