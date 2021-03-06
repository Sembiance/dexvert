"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Pentax RAW",
	website  : "http://fileformats.archiveteam.org/wiki/Pentax_PEF",
	ext      : [".pef", ".ptx"],
	magic    : ["Pentax RAW image"],
	mimeType : "image/x-pentax-pef"
};

exports.converterPriorty = ["darktable-cli", "convert", "abydosconvert", "nconvert"];

exports.inputMeta = (state, p, cb) => p.family.darkTableInputMeta(state, p, cb);
