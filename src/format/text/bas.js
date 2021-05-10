"use strict";
const XU = require("@sembiance/xu"),
	C = require("../../C.js");

exports.meta =
{
	name           : "BASIC Source File",
	website        : "http://fileformats.archiveteam.org/wiki/BASIC",
	ext            : [".bas"],
	forbidExtMatch : true,
	magic          : C.TEXT_MAGIC,
	weakMagic      : true,
	untouched      : true
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
