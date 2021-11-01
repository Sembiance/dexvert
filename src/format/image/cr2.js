"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Canon RAW 2",
	website  : "http://fileformats.archiveteam.org/wiki/Canon_RAW_2",
	ext      : [".cr2"],
	magic    : ["Canon RAW 2 format", "Canon CR2 raw image data"],
	mimeType : "image/x-canon-cr2"
};

exports.converterPriority = ["darktable-cli", "convert", "abydosconvert", "nconvert"];

exports.inputMeta = (state, p, cb) => p.family.darkTableInputMeta(state, p, cb);
