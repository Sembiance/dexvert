"use strict";
const XU = require("@sembiance/xu"),
	C = require("../../C.js");

// txtByExt handles files with specific extensions that are likely text but have non-ascii characters which requires loosened magic match of A.GENERIC_MAGIC which includes "data"
exports.meta =
{
	name      : "Text File",
	website   : "http://fileformats.archiveteam.org/wiki/Text",
	magic     : [...C.TEXT_MAGIC, ...C.GENERIC_MAGIC],
	weakMagic : true,
	priority  : C.PRIORITY.VERYLOW,
	ext       :
	[
		".txt", ".rea", ".doc", ".docs", ".english", ".credits", ".manual", ".man", ".info", ".inf", ".log",
		".cfg", ".config",
		".78x20", ".78*20", ".38x20", ".38x17", ".36x20", ".36*20", ".advert", ".advert2"
	],
	untouched : true
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
