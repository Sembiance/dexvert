"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Microsoft Windows Cursor",
	website  : "http://fileformats.archiveteam.org/wiki/CUR",
	ext      : [".cur"],
	mimeType : "application/ico",
	magic    : ["MS Windows cursor resource", "Microsoft Windows Cursor"]
};

exports.converterPriorty = ["deark"];
