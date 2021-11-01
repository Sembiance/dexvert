"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Soundtracker Pro II Module",
	ext     : [".stp"],
	magic   : ["Spectrum Sound Tracker Pro 2 chiptune"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["zxtune123", "openmpt123"];
