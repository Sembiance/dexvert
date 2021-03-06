"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Epson RAW File",
	website  : "http://fileformats.archiveteam.org/wiki/ERF",
	ext      : [".erf"],
	magic    : ["Epson Raw Image Format", /^TIFF image data.*description=EPSON DSC/],
	mimeType : "image/x-epson-erf"
};

exports.converterPriorty = ["darktable-cli", "convert", "abydosconvert", "nconvert"];

exports.inputMeta = (state, p, cb) => p.family.darkTableInputMeta(state, p, cb);
