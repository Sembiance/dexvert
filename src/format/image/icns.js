"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "MacOS Icon",
	website  : "http://fileformats.archiveteam.org/wiki/ICNS",
	ext      : [".icns"],
	mimeType : "image/x-icns",
	magic    : ["Mac OS X icon", "Apple Icon Image Format"]
};

exports.converterPriorty = ["deark", "abydosconvert"];
