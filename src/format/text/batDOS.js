"use strict";
const XU = require("@sembiance/xu"),
	C = require("../../C.js");

exports.meta =
{
	name           : "DOS Batch File",
	website        : "http://fileformats.archiveteam.org/wiki/BAT",
	ext            : [".bat"],
	forbidExtMatch : true,
	magic          : ["DOS batch file", ...C.TEXT_MAGIC, /^data$/],
	weakMagic      : true,
	untouched      : true,
	hljsLang       : "bat"
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
