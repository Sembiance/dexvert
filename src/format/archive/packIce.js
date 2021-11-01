"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Pack-Ice Archive",
	website : "http://fileformats.archiveteam.org/wiki/Pack-Ice",
	magic   : ["Pack-Ice compressed data"]
};

exports.converterPriority = ["unice68"];
