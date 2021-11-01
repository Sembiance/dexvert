"use strict";
const XU = require("@sembiance/xu"),
	C = require("../../C.js");

exports.meta =
{
	name     : "SoundTracker Module",
	ext      : [".mod"],
	priority : C.PRIORITY.LOW
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["xmp", "uade123", "zxtune123", "openmpt123"];
