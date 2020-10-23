"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Kodak Pro Digital RAW",
	website  : "http://fileformats.archiveteam.org/wiki/Kodak",
	ext      : [".dcr"],
	magic    : ["Kodak Digital Camera Raw Image File"],
	mimeType : "image/x-kodak-dcr"
};

exports.converterPriorty = ["abydosconvert"];
