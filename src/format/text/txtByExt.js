"use strict";
const XU = require("@sembiance/xu"),
	C = require("../../C.js");

// txtByExt handles files with specific extensions that are likely text but have non-ascii characters which requires loosened magic match of /^data$/
exports.meta =
{
	name           : "Text File",
	website        : "http://fileformats.archiveteam.org/wiki/Text",
	magic          : Array.from(C.TEXT_MAGIC),
	forbiddenMagic : ["TROFF markup"],
	weakMagic      : true,
	priority       : C.PRIORITY.VERYLOW,
	ext            :
	[
		".txt", ".rea", ".doc", ".docs", ".english", ".credits", ".info", ".inf", ".log", ".ascii", ".nfo",
		".cfg", ".config",
		".frm", ".hlp",
		".advert", ".advert2"
	],
	forbidExtMatch : true,
	untouched      : true,
	fallback       : true
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
