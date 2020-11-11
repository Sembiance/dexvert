"use strict";
const XU = require("@sembiance/xu"),
	C = require("../../C.js");

exports.meta =
{
	name           : "Cascading Style Sheet File",
	website        : "http://fileformats.archiveteam.org/wiki/CSS",
	ext            : [".css"],
	mimeType       : "text/css",
	forbidExtMatch : true,
	magic          : [...C.TEXT_MAGIC, "assembler source"],	// Sadly file often detects it as assembler source and no other indentifiers come back with magic
	weakMagic      : true,
	untouched      : true,
	hljsLang       : "css"
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
