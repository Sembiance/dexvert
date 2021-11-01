"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "Sound Programming Language Module",
	ext   : [".spl"],
	magic : ["SOPROL Sound Programming Language module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123"];
