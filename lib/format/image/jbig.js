"use strict";
const XU = require("@sembiance/xu");
exports.meta =
{
	name     : "Joint Bi-Level Image experts Group",
	website  : "http://fileformats.archiveteam.org/wiki/JBIG",
	ext      : [".jbg", ".jbig", ".bie"],
	magic    : ["JBIG raster bitmap"]
};

exports.converterPriorty = ["convert"];
