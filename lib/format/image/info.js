"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Amiga Workbench Icon",
	website  : "http://fileformats.archiveteam.org/wiki/Amiga_Workbench_icon",
	ext      : [".info"],
	magic    : [/^Amiga Workbench.* icon$/, "Amiga Workbench project icon", "Amiga NewIcon"]
};

exports.converterPriorty = ["deark"];
