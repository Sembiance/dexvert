"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "OS/2 Pointer",
	website  : "http://fileformats.archiveteam.org/wiki/OS/2_Pointer",
	ext      : [".ptr"],
	magic    : ["OS/2 Pointer", /^OS\/2 [12].x color pointer/]
};

exports.converterPriority = ["deark"];
