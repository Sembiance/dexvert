"use strict";
const XU = require("@sembiance/xu"),
	C = require("../../C.js");

exports.meta =
{
	name      : "Lingo Script",
	website   : "http://fileformats.archiveteam.org/wiki/CSS",
	filename  : [/^lingoScript$/],
	magic     : C.TEXT_MAGIC,
	weakMagic : true
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
