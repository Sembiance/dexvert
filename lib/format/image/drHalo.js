"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	C = require(path.join(__dirname, "..", "..", "C.js"));

exports.meta =
{
	name     : "Dr. Halo",
	website  : "http://fileformats.archiveteam.org/wiki/Dr._Halo",
	ext      : [".cut", ".pal", ".pic"],
	priority : C.PRIORITY.LOW
};

exports.converterPriorty = ["convert"];
