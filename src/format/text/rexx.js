"use strict";
const XU = require("@sembiance/xu"),
	C = require("../../C.js");

exports.meta =
{
	name           : "OS/2 REXX Batch file",
	website        : "https://www.tutorialspoint.com/rexx/index.htm",
	ext            : [".cmd", ".rexx", ".rex"],
	forbidExtMatch : true,
	magic          : ["OS/2 REXX batch file", ...C.TEXT_MAGIC],
	weakMagic      : true,
	untouched      : true
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
