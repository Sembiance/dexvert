"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name : "Speedy A1 System Module",
	ext  : [".sas"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123"];
