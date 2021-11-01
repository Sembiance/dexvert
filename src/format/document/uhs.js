"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Universal Hint System Document",
	website  : "http://fileformats.archiveteam.org/wiki/UHS",
	ext      : [".uhs"],
	magic    : ["Universal Hint System"]
};

exports.converterPriority = ["uhs2html"];
