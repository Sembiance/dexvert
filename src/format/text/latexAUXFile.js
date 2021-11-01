"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Latex Auxiliary File",
	ext            : [".aux"],
	forbidExtMatch : true,
	magic          : ["LaTeX auxiliary file"],
	weakMagic      : true,
	untouched      : true
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
