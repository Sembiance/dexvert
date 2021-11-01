"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "Beathoven Synthesizer Module",
	ext   : [".bss"],
	magic : ["Beathoven Synthesizer module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123"];
