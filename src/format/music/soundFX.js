"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "SoundFX Module",
	website : "http://fileformats.archiveteam.org/wiki/SoundFX_module",
	ext     : [".sfx", ".sfx2"],
	magic   : [/^SoundFX [Mm]odule/]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["xmp", "uade123", "zxtune123", "openmpt123"];
