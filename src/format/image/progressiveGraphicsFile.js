"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "Progressive Graphics File",
	website     : "http://fileformats.archiveteam.org/wiki/PGF_(Progressive_Graphics_File)",
	ext         : [".pgf"],
	magic       : ["Progressive Graphics image data"],
	mimeType    : "image/x-pgf"
};

exports.converterPriority = ["pgf"];
