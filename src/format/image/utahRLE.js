"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Utah RLE",
	website : "http://fileformats.archiveteam.org/wiki/Utah_RLE",
	ext     : [".rle"],
	magic   : ["Utah Raster Toolkit bitmap", "RLE image data"]
};

exports.converterPriority = ["convert", "recoil2png"];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
