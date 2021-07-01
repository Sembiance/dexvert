"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs"),
	C = require("../../C.js");

exports.meta =
{
	name           : "File List",
	magic          : [...C.TEXT_MAGIC, /^data$/],
	weakMagic      : true,
	priority       : C.PRIORITY.LOW,
	ext            : [".bbs", ".lst", ".lis", ".dir", ".ind"],
	filename       : [/^dir\.?\d+$/i, /files.\d+$/i, /^files\.txt$/i],
	untouched      : true,
	confidenceAdjust : (state, matchType, curConfidence) => -(curConfidence-60)	// 'data' can match almost anything, so let's lower our confidence so this is more of a fallback
};

exports.idCheck = state => fs.statSync(state.input.absolute).size<XU.MB*25;	// Unlikely to ever encountere a file list this big

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
