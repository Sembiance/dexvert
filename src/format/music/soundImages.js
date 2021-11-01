"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name : "Sound Images Module",
	ext  : [".tw"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123"];
