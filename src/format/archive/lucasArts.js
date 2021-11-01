"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "Lucas Arts Game Data Archive",
	ext   : [".gob"],
	magic : ["LucasArts Game data archive"]
};

exports.converterPriority = ["gameextractor"];
