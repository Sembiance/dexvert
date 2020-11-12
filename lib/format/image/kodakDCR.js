"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Kodak Pro Digital RAW",
	website  : "http://fileformats.archiveteam.org/wiki/Kodak",
	ext      : [".dcr"],
	magic    : [/^TIFF image data.*manufacturer=Kodak/],
	mimeType : "image/x-kodak-dcr"
};

exports.converterPriorty = ["abydosconvert"];
