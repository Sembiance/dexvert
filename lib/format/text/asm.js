"use strict";
const XU = require("@sembiance/xu"),
	C = require("../../C.js");

exports.meta =
{
	name           : "Assembly Source File",
	website        : "http://fileformats.archiveteam.org/wiki/Assembly_language",
	ext            : [".asm"],
	forbidExtMatch : true,
	magic          : [...C.TEXT_MAGIC, "C source"], // file often confuses assembly for C source and nothing else identifies it
	weakMagic      : true,
	untouched      : true,
	hljsLang       : "x86asm"
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
