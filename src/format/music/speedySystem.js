"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "Speedy System Module",
	ext   : [".ss"],
	magic : ["Speedy System module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123"];
