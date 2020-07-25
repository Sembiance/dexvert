"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Encapsulated PostScript",
	website  : "http://fileformats.archiveteam.org/wiki/EPS",
	ext      : [".eps", ".epsf", ".epsi", ".epi", ".ept"],
	mimeType : "application/postscript",
	magic    : ["Encapsulated PostScript File Format"]
};

exports.converterPriorty = ["nconvert"];
