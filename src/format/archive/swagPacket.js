"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "SWAG Packet",
	website : "http://fileformats.archiveteam.org/wiki/SWG",
	ext     : [".swg"],
	magic   : ["Swag archive data", "Swag Reader Packet"]
};

exports.converterPriority =
[
	["swagv", "swagReader"]
];
