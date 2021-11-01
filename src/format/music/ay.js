"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "AY Amadeus Chiptune",
	ext   : [".ay", ".emul"],
	magic : ["Spectrum 128 tune", "AY chiptune"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["zxtune123"];
