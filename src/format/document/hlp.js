"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "Windows Help File",
	website     : "http://fileformats.archiveteam.org/wiki/HLP",
	ext         : [".hlp"],
	magic       : ["Windows HELP File", /^MS Windows 3\.. help/, "Windows Help File"]
};

exports.converterPriority = ["helpdeco", "UniExtract"];
