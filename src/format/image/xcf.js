"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "The GIMP Image Format",
	website  : "http://fileformats.archiveteam.org/wiki/XCF",
	ext      : [".xcf"],
	mimeType : "image/x-xcf",
	magic    : ["The GIMP image format", "GIMP XCF image data", "Gimp Image File Format"]
};

exports.converterPriority = ["xcf2png"];
