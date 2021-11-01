"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "Anders 0land Module",
	ext   : [".hot"],
	magic : ["Anders 0land music"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123"];
