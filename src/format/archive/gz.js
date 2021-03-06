"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "GZip archive",
	website : "http://fileformats.archiveteam.org/wiki/GZ",
	ext     : [".gz", ".gzip", ".z"],
	magic   : ["gzip compressed data", "GZipped data", "UNIX compressed data", "compress'd data"]
};

exports.converterPriorty = ["gunzip"];
