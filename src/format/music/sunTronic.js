"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "SUNTronic Module",
	ext   : [".sun"],
	magic : ["SUNTronic module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123"];
