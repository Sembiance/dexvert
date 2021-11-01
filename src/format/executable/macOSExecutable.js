"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "MacOS Executable",
	website : "http://fileformats.archiveteam.org/wiki/MacBinary",
	magic   : ["Macintosh Application (MacBinary)", "Preferred Executable Format"]
};

exports.converterPriority = ["unar", "deark"];
