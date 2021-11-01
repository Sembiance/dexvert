"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Minolta RAW",
	website  : "http://fileformats.archiveteam.org/wiki/Minolta",
	ext      : [".mrw"],
	magic    : ["Minolta RAW", "Minolta Dimage camera raw", "Minolta Dimage RAW image"],
	mimeType : "image/x-minolta-mrw"
};

exports.converterPriority = ["darktable-cli", "convert", "abydosconvert", "nconvert"];

exports.inputMeta = (state, p, cb) => p.family.darkTableInputMeta(state, p, cb);
