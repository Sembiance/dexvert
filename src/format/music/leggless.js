"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "Leggless Music Editor Module",
	ext   : [".lme"],
	magic : ["Leggless Music Editor module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123"];
