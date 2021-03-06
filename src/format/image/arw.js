"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Sony RAW",
	website  : "http://fileformats.archiveteam.org/wiki/Sony_ARW",
	ext      : [".arw"],
	magic    : ["Sony ARW RAW Image File", "Sony digital camera RAW image"],
	mimeType : "image/x-sony-arw"
};

exports.converterPriorty = ["darktable-cli", "convert", "abydosconvert", "nconvert"];

exports.inputMeta = (state, p, cb) => p.family.darkTableInputMeta(state, p, cb);
