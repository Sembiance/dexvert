"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name : "Voodoo Supreme Synthesizer Module",
	ext  : [".vss"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123"];
