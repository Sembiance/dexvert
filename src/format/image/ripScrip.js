"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Remote Imaging Protocol Script",
	website : "http://fileformats.archiveteam.org/wiki/RIPscrip",
	ext     : [".rip"],
	magic   : ["RIPscript"]
};

exports.converterPriority = ["pabloDrawConsole"];
