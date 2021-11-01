"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "Rob Hubbard Module",
	ext   : [".rh", ".rho"],
	magic : ["Rob Hubbard chiptune", "Rob Hubbard ST module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123"];
