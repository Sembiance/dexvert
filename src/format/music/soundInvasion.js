"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "Sound Invasion Module",
	ext   : [".is", ".is20"],
	magic : ["Sound Invasion Music System module", "Sound Invasion Music System 2.0 module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123"];
