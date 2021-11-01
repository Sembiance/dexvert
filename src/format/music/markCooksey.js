"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "Mark Cooksey Module",
	ext   : [".mc"],
	magic : ["Mark Cooksey module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123"];
