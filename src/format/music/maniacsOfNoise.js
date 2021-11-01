"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "Maniacs of Noise Module",
	ext   : [".mon"],
	magic : ["M.O.N New module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123"];
