"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "WAD2",
	website : "http://www.gamers.org/dEngine/quake/spec/quake-spec34/qkspec_7.htm",
	ext     : [".wad"],
	magic   : ["WAD2 file"]
};

exports.converterPriority = ["gameextractor"];
