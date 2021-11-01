"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "OS/2 Help File",
	website     : "http://fileformats.archiveteam.org/wiki/INF/HLP_(OS/2)",
	ext         : [".hlp", ".inf"],
	magic       : ["OS/2 HLP", "OS/2 Help"]
};

exports.converterPriority = ["ipf2txt"];
