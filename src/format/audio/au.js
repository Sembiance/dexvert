"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Sun Microsystems Audio File",
	website  : "http://fileformats.archiveteam.org/wiki/AU",
	ext      : [".au", ".snd"],
	magic    : ["NeXT/Sun sound", "Sun/NeXT audio data", "NeXT/Sun uLaw/AUdio format"],
	mimeType : "audio/basic"
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["sox"];
