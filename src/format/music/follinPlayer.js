"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "Follin Player Module",
	ext   : [".tf"],
	magic : ["Follin Player II module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123"];
