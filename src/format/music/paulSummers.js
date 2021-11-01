"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name : "Paul Summers Module",
	ext  : [".snk"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123"];
