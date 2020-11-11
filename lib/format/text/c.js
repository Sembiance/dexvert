"use strict";
const XU = require("@sembiance/xu"),
	C = require("../../C.js");

exports.meta =
{
	name           : "C Source or Header File",
	website        : "http://fileformats.archiveteam.org/wiki/C",
	ext            : [".c", ".h"],
	forbidExtMatch : true,
	magic          : ["C source"],
	priority       : C.PRIORITY.HIGH,
	weakMagic      : true,
	untouched      : true,
	hljsLang       : "cpp"
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
