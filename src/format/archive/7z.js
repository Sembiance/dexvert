"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "7-Zip Archive",
	website  : "http://fileformats.archiveteam.org/wiki/7z",
	ext      : [".7z"],
	mimeType : "application/x-7z-compressed",
	magic    : ["7Zip format", "7-zip archive data", "7-Zip compressed archive"]
};

exports.converterPriorty = ["7z"];
