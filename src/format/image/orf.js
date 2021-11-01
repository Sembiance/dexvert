"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Olympus RAW",
	website  : "http://fileformats.archiveteam.org/wiki/ORF",
	ext      : [".orf"],
	magic    : ["Olympus RAW", "Olympus ORF raw image data", "Olympus digital camera RAW image"],
	mimeType : "image/x-olympus-orf"
};

exports.converterPriority = ["darktable-cli", "convert", "abydosconvert", "nconvert"];

exports.inputMeta = (state, p, cb) => p.family.darkTableInputMeta(state, p, cb);
