"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "Synthesis Module",
	ext   : [".syn"],
	magic : [/^Synthesis [Mm]odule/]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123"];
