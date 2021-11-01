"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "Sound Master Module",
	ext   : [".sm", ".smpro", ".sm3"],
	magic : ["Sound Master II module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123"];
