"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Fujifilm RAW",
	website  : "http://fileformats.archiveteam.org/wiki/RAF",
	ext      : [".raf"],
	magic    : ["Fujifilm Raw image"],
	mimeType : "image/x-fuji-raf"
};

exports.converterPriority = ["darktable-cli", "convert", "abydosconvert", "nconvert"];

exports.inputMeta = (state, p, cb) => p.family.darkTableInputMeta(state, p, cb);
