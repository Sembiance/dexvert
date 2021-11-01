"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "Delitracker Customplay Module",
	ext   : [".cus"],
	magic : ["Delitracker Customplay Module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123"];
