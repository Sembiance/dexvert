"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Macintosh Picture Format",
	website  : "http://fileformats.archiveteam.org/wiki/PICT",
	ext      : [".pict", ".pic", ".pct"],
	mimeType : "image/pict",
	magic    : ["QuickDraw/PICT bitmap", "Macintosh PICT Image"]
};

exports.converterPriorty = ["deark", "recoil2png"];
