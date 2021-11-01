"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Portable Greyscale",
	website  : "http://fileformats.archiveteam.org/wiki/PGM",
	ext      : [".pgm"],
	mimeType : "image/x-portable-graymap",
	magic    : ["Portable GrayMap bitmap", "Portable Grey Map", /^Netpbm image data .*greymap$/]
};

exports.converterPriority = ["convert"];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
