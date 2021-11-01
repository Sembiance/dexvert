"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "GX1 Bitmap",
	website  : "http://fileformats.archiveteam.org/wiki/GX1",
	ext      : [".gx1"],
	mimeType : "image/x-gx1",
	magic    : ["GX1 bitmap"]
};

exports.converterPriority = ["abydosconvert"];
