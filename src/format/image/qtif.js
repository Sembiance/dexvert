"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "QuickTime Image Format",
	website  : "http://fileformats.archiveteam.org/wiki/QTIF",
	ext      : [".qtif", ".qif"],
	mimeType : "image/qtif",
	magic    : ["QuickTime Image Format"],
	notes    : "Not all QTIF sub formats are not supported."
};

exports.converterPriorty = ["nconvert", "deark", "abydosconvert"];
