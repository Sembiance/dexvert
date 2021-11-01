"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "Howie Davies Module",
	ext   : [".hd"],
	magic : ["Howie Davies module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123"];
