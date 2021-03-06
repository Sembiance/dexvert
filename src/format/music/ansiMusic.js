"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "ANSI Music",
	website        : "http://artscene.textfiles.com/ansimusic/",
	ext            : [".mus"],
	forbidExtMatch : true,
	magic          : ["ANSI escape sequence text", "ISO-8859 text, with CRLF, CR, LF line terminators, with escape sequences"],
	weakMagic      : true,
	unsupported    : true
};
