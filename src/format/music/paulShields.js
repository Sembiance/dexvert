"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name : "Paul Shields Module",
	ext  : [".ps"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123"];
