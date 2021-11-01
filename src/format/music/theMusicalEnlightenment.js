"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name : "The Musical Enlightenment Module",
	ext  : [".tme"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123"];
