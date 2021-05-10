"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "C/C++ Source or Header",
	website        : "http://fileformats.archiveteam.org/wiki/C",
	ext            : [".c", ".h", ".cpp", ".cxx", ".cc", ".c++", ".hpp"],
	forbidExtMatch : true,
	magic          : ["C source", "C++ source"],
	weakMagic      : true,
	untouched      : true,
	hljsLang       : "cpp"
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
