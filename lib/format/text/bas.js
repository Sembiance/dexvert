"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	C = require(path.join(__dirname, "..", "..", "C.js"));

exports.meta =
{
	name           : "BASIC Source File",
	website        : "http://fileformats.archiveteam.org/wiki/BASIC",
	ext            : [".bas"],
	forbidExtMatch : true,
	magic          : C.TEXT_MAGIC,
	weakMagic      : true
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
