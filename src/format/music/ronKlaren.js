"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "Ron Klaren Module",
	ext   : [".rk"],
	magic : ["Ron Klaren module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123"];
