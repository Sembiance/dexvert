"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Kodak DC25",
	website  : "http://fileformats.archiveteam.org/wiki/Kodak",
	ext      : [".k25"],
	fileSize : [77888, 140352],
	magic    : [/^TIFF image data.*model=KODAK DC25/],
	mimeType : "image/x-kodak-k25"
};

exports.converterPriority = ["abydosconvert"];
