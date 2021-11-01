"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name      : "HA Archive",
	website   : "http://fileformats.archiveteam.org/wiki/HA",
	ext       : [".ha"],
	magic     : ["HA compressed archive", "HA archive data"],
	weakMagic : ["HA compressed archive"]
};

exports.converterPriority = ["ha"];
