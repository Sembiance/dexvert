"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Quake PAK",
	website : "http://fileformats.archiveteam.org/wiki/Quake_PAK",
	ext     : [".pak"],
	magic   : ["Quake archive"]
};

exports.converterPriority = ["gameextractor"];
