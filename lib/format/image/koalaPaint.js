"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Koala Paint",
	website  : "http://fileformats.archiveteam.org/wiki/PCX",
	ext      : [".gig", ".koa", ".kla"],
	mimeType : "image/x-koa",
	magic    : ["Koala Paint"]
};

exports.converterPriorty = ["abydosconvert", "nconvert"];
