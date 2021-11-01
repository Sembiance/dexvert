"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name : "V2 Module",
	ext  : [".v2m"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["zxtune123"];
