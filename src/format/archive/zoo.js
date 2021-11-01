"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Zoo Archive",
	website : "http://fileformats.archiveteam.org/wiki/Zoo",
	ext     : [".zoo"],
	magic   : ["ZOO compressed archive", "Zoo archive data"]
};

exports.converterPriority = ["zoo", "deark", "UniExtract"];
