"use strict";
const XU = require("@sembiance/xu"),
	C = require("../../C.js");

exports.meta =
{
	name           : "Pascal/Delphi Source File",
	website        : "http://fileformats.archiveteam.org/wiki/Pascal",
	ext            : [".pas", ".tp5"],
	forbidExtMatch : true,
	magic          : [...C.TEXT_MAGIC, "Delphi Project source"],
	weakMagic      : true,
	untouched      : true,
	hljsLang       : "delphi"
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
