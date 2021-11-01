"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "EarAche Module",
	ext   : [".ea"],
	magic : ["EarAche module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123"];
