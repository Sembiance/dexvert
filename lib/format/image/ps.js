"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "PostScript",
	website     : "http://fileformats.archiveteam.org/wiki/Postscript",
	ext         : [".ps"],
	mimeType    : "application/postscript",
	magic       : [/^PostScript$/, /^PostScript document/],
	bruteUnsafe : true
};

exports.converterPriorty = ["inkscape", "uniconvertor", "abydosconvert", "nconvert"];
