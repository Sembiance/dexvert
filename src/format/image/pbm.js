"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Portable Bitmap",
	website  : "http://fileformats.archiveteam.org/wiki/PBM",
	ext      : [".pbm"],
	mimeType : "image/x-portable-bitmap",
	magic    : ["Portable BitMap", "Portable Bitmap Image", /^Netpbm image data .*bitmap$/]
};

exports.converterPriority = ["convert"];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
