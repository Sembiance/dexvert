"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name : "Quartet PSG Module",
	ext  : [".sqt"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123"];
