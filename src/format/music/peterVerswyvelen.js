"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name : "Peter Verswyvelen Module",
	ext  : [".pvp"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123"];
