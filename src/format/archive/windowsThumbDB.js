"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Windows Thumbnail Database",
	website  : "http://fileformats.archiveteam.org/wiki/Thumbs.db",
	ext      : [".db"],
	filename : ["Thumbs.db"],
	magic    : ["Windows Thumbnail Database"]
};

exports.converterPriority = ["deark", "vinetto"];
