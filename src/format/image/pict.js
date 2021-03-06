"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Macintosh Picture Format",
	website        : "http://fileformats.archiveteam.org/wiki/PICT",
	ext            : [".pict", ".pic", ".pct"],
	forbidExtMatch : true,
	mimeType       : "image/pict",
	magic          : ["QuickDraw/PICT bitmap", "Macintosh PICT Image", "Claris clip art"]
};

exports.converterPriorty = ["deark", "recoil2png", "nconvert", "convert", "soffice"];
