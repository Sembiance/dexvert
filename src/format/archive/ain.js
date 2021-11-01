"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "AIN Archive",
	website : "http://fileformats.archiveteam.org/wiki/AIN",
	ext     : [".ain"],
	magic   : ["AIN compressed archive"]
};

exports.converterPriority = ["ain"];
