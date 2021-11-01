"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Magick Image File Format",
	website  : "http://fileformats.archiveteam.org/wiki/MIFF",
	ext      : [".miff", ".mif"],
	mimeType : "image/x-miff",
	magic    : ["MIFF image data", "ImageMagick Machine independent File Format bitmap"]
};

exports.converterPriority = ["convert", "nconvert"];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
