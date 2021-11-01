"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name         : "PostScript",
	website      : "http://fileformats.archiveteam.org/wiki/Postscript",
	ext          : [".ps"],
	mimeType     : "application/postscript",
	magic        : [/^PostScript$/, /^PostScript document/],
	forbiddenExt : [".eps"],
	unsafe       : true
};

exports.converterPriority = ["ps2pdf"];	//, "inkscape", "uniconvertor", "abydosconvert", "nconvert"];
