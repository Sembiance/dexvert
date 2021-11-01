"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Farallon Replica Document",
	website : "http://fileformats.archiveteam.org/wiki/Farallon_Replica",
	ext     : [".rpl"],
	magic   : ["Farallon Replica document"]
};

exports.converterPriority = ["replica"];
