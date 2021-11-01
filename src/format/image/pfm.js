"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Portable Float Map",
	website  : "http://fileformats.archiveteam.org/wiki/PFM",
	ext      : [".pfm"],
	mimeType : "image/x-portable-floatmap",
	magic    : ["Portable Float Map color bitmap"]
};

exports.converterPriority = ["convert", "abydosconvert", "nconvert"];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
