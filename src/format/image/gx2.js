"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "GX2 Bitmap",
	website  : "http://fileformats.archiveteam.org/wiki/GX2",
	ext      : [".gx2"],
	mimeType : "image/x-gx2",
	magic    : ["GX2 bitmap"]
};

exports.converterPriority = ["abydosconvert"];
