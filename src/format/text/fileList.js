"use strict";
const XU = require("@sembiance/xu"),
	C = require("../../C.js");

exports.meta =
{
	name      : "File List",
	magic     : [...C.TEXT_MAGIC, ...C.GENERIC_MAGIC],
	weakMagic : true,
	priority  : C.PRIORITY.LOW,
	ext       : [".bbs", ".lst", ".lis", ".dir", ".ind"],
	filename  : [/^dir\.?\d+$/i, /files.\d+$/i, "files.txt"],
	untouched : true
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
