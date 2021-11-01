"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "You Don't Know Jack Archive",
	ext     : [".srf"],
	magic   : ["You Don't Know Jack game data archive"]
};

exports.converterPriority = ["gameextractor"];
