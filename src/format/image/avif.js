"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "AV1 Image File Format",
	website  : "http://fileformats.archiveteam.org/wiki/AVIF",
	ext      : [".avif", ".avifs"],
	mimeType : "image/avif",
	magic    : ["AV1 Image File Format bitmap"]
};

exports.converterPriority = ["avifdec", "abydosconvert"];
