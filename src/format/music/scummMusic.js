"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name : "SCUMM Music Module",
	ext  : [".scumm"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123"];
