"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Krita",
	website  : "http://fileformats.archiveteam.org/wiki/Krita",
	ext      : [".kra"],
	mimeType : "application/x-krita",
	magic    : [/^Krita [Dd]ocument/]
};

exports.converterPriority = ["deark"];
