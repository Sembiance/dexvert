"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "Janko Mrsic-Flogel Module",
	ext   : [".jmf"],
	magic : ["Janko Mrsic-Flogel module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123"];
