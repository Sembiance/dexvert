"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Digital Picture Exchange",
	website  : "http://fileformats.archiveteam.org/wiki/DPX",
	ext      : [".dpx"],
	mimeType : "image/x-digital-picture-exchange",
	magic    : [/^Digital Moving Picture Exchange [Bb]itmap/, "DPX image data"]
};

exports.converterPriorty = ["convert", "abydosconvert", "nconvert"];
