"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs"),
	C = require("../../C.js");

exports.meta =
{
	name      : "File List",
	magic     : C.TEXT_MAGIC,
	weakMagic : true,
	priority  : C.PRIORITY.LOW,
	ext       : [".bbs", ".lst", ".lis", ".dir", ".ind"],
	filename  : [/^dir\.?\d+$/i, /files.\d+$/i, /^files\.txt$/i, /^\d+_index.txt$/, /^[a-zA-Z]_index.txt$/],
	untouched : true
};

exports.idCheck = state => fs.statSync(state.input.absolute).size<XU.MB*25;	// Unlikely to ever encountere a file list this big

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
