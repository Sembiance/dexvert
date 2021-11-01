"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Audio Interchange File Format",
	website : "http://fileformats.archiveteam.org/wiki/AIFF",
	ext     : [".aif", ".aiff", ".aff"],
	magic   : ["AIFF Audio Interchange File Format", "IFF data, AIFF audio", "Audio Interchange File Format"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["sox", "ffmpeg", "vgmstream"];
