"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Open XML Paper Specification",
	website : "http://fileformats.archiveteam.org/wiki/XPS",
	ext     : [".xps", ".oxps"],
	magic   : ["Open XML Paper Specification"]
};

exports.converterPriorty = ["xpstopdf"];
