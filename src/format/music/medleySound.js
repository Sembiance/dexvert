"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "MedleySound Module",
	ext   : [".mso"],
	magic : ["MedlySound module"]	// trid appears to misspell this
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123"];
