"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "AMOS Icons Bank",
	website  : "http://fileformats.archiveteam.org/wiki/AMOS_Icon_Bank",
	ext      : [".abk"],
	mimeType : "image/x-amos-iconbank",
	magic    : ["AMOS Icons Bank"]
};

exports.converterPriority = ["deark"];
