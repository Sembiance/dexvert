"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Makefile",
	website        : "http://fileformats.archiveteam.org/wiki/CSS",
	ext            : [".mak"],
	forbidExtMatch : true,
	filename       : [/^[Mm]akefile[._-].*/, /^[Mm]akefile$/],
	magic          : ["makefile script"],
	weakMagic      : true,
	untouched      : true,
	hljsLang       : "makefile"
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
