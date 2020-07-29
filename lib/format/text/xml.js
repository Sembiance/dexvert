"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Extensible Markup Language",
	website        : "http://fileformats.archiveteam.org/wiki/XML",
	ext            : [".xml"],
	forbidExtMatch : true,
	mimeType       : "application/xml",
	magic          : ["Extensible Markup Language", "Generic XML", /^XML .*document/],
	weakMagic      : true
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
