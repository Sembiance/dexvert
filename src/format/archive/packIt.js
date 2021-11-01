"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "PackIt Archive",
	website : "http://fileformats.archiveteam.org/wiki/PackIt",
	ext     : [".pit"],
	magic   : ["PackIt compressed archive"]
};

exports.converterPriority = ["unar"];
