"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "SynTracker Module",
	ext   : [".synmod"],
	magic : ["SynTracker module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123"];
