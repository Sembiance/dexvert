"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Stuffit Archive",
	website : "http://fileformats.archiveteam.org/wiki/SIT",
	ext      : [".sit"],
	magic    : ["StuffIt compressed archive", /StuffIt Archive/]
};

exports.converterPriority = ["unar", "UniExtract"];
