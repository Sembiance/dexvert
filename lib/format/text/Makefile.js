"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Makefile",
	website        : "http://fileformats.archiveteam.org/wiki/CSS",
	ext            : [".mak"],
	forbidExtMatch : true,
	filename       : [/^[Mm]akefile\..*/, /^[Mm]akefile$/],
	magic          : ["makefile script"],
	weakMagic      : true
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
