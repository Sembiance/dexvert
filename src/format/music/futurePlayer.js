"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "FuturePlayer Module",
	ext   : [".fp"],
	magic : ["FuturePlayer module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123"];
