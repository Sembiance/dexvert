"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name : "Tomy Tracker Module",
	ext  : [".sg"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123"];
