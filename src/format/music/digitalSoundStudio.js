"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "Digital Sound Studio Module",
	ext   : [".dss"],
	magic : ["Digital Sound Studio module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123"];
