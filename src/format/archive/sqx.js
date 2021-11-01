"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Squeez SQX Archive",
	website : "http://fileformats.archiveteam.org/wiki/SQX",
	ext     : [".sqx"],
	magic   : ["SQX compressed archive"]
};

exports.converterPriority = ["sqc"];
