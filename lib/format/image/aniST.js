"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Ani ST",
	website  : "http://fileformats.archiveteam.org/wiki/AniST",
	ext      : [".scr", ".str"],
	mimeType : "image/x-ani-st"
};

exports.converterPriorty = ["abydosconvert"];
exports.converterExclude = ["convert"];
