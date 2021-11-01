"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "Riff Raff Module",
	ext   : [".riff"],
	magic : ["Riff Raff module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123"];
