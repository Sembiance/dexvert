"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Cabinet",
	website : "http://fileformats.archiveteam.org/wiki/CAB2",
	ext     : [".cab"],
	magic   : [/^Microsoft Cabinet [Aa]rchive/]
};

exports.converterPriority = ["cabextract", "UniExtract"];
