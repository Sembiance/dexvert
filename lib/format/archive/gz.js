"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "GZip archive",
	website : "http://fileformats.archiveteam.org/wiki/GZ",
	ext     : [".gz", ".gzip"],
	magic   : ["gzip compressed data", "GZipped data"]
};

exports.steps = [() => ({program : "gunzip"})];
