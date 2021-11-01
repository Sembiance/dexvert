"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "Mike Davies Module",
	ext   : [".md"],
	magic : ["Mike Davies module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123"];
