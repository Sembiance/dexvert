"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "C Source or Header File",
	website        : "http://fileformats.archiveteam.org/wiki/C",
	ext            : [".c", ".h"],
	forbidExtMatch : true,
	magic          : ["C source"],
	weakMagic      : true
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
