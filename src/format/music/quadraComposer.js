"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "Quadra Composer",
	ext   : [".emod"],
	magic : ["Quadra Composer module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["zxtune123", "uade123"];
