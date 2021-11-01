"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "GrafX2",
	website  : "http://grafx2.chez.com/",
	ext      : [".pkm"],
	magic    : ["GrafX2 bitmap"],
	mimeType : "image/x-pkm"
};

exports.converterPriority = ["abydosconvert"];
