"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "C++ Source File",
	website        : "http://fileformats.archiveteam.org/wiki/AIFF",
	ext            : [".cpp", ".cxx", ".cc", ".c++", ".hpp"],
	forbidExtMatch : true,
	magic          : ["C++ source", "C source"],
	untouched      : true
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
