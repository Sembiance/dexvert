"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name : "Sound Control Module",
	ext  : [".sc"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123"];
