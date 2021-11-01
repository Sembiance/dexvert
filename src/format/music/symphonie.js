"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "Symphonie Module",
	ext   : [".symmod"],
	magic : ["Symphonie SymMOD music file", "Symphonie Module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["zxtune123"];
