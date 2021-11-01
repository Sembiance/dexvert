"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Octalyser Module",
	ext     : [".mod"],
	magic   : [/^Octalyser \d-channel STe\/Falcon Module$/]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["xmp", "zxtune123", "openmpt123"];
