"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "PC Paintbrush Image",
	website  : "http://fileformats.archiveteam.org/wiki/PCX",
	ext      : [".pcx"],
	mimeType : "image/x-pcx",
	magic    : ["PCX bitmap", /^PCX ver.* image data/, /^PCX$/]
};

exports.converterPriorty = ["nconvert", "convert"];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
