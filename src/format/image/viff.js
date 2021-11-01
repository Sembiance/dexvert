"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Khoros Visualization Image",
	website  : "http://fileformats.archiveteam.org/wiki/VIFF",
	ext      : [".viff", ".xv"],
	mimeType : "image/x-viff",
	magic    : ["Khoros Visualization Image File Format"]
};

exports.converterPriority = ["convert", "abydosconvert"];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
