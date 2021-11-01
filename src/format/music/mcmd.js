"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "MCMD Module",
	ext   : [".mcmd"],
	magic : ["MCMD module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123"];
