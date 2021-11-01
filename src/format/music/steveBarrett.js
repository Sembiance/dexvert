"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name : "Steve Barrett Module",
	ext  : [".sb"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123"];
