"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Panasonic RAW",
	website  : "http://fileformats.archiveteam.org/wiki/Panasonic_RAW",
	ext      : [".rw2", ".raw", ".rwl"],
	magic    : ["Panasonic RAW image", "Panasonic Raw", "Leica RAW image"],
	mimeType : "image/x-panasonic-raw"
};

exports.converterPriorty = ["darktable-cli", "convert", "abydosconvert", "nconvert"];

exports.inputMeta = (state, p, cb) => p.family.darkTableInputMeta(state, p, cb);
