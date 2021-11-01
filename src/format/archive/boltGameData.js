"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "BOLT Game Data Archive",
	ext   : [".blt"],
	magic : ["BOLT game data archive"]
};

exports.converterPriority = ["gameextractor"];
