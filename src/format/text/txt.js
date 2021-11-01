"use strict";
const XU = require("@sembiance/xu"),
	C = require("../../C.js");

// Fallback match for anything that is just text. This will only be matched as a last resort
exports.meta =
{
	name      : "Text File",
	website   : "http://fileformats.archiveteam.org/wiki/Text",
	magic     : C.TEXT_MAGIC,
	priority  : C.PRIORITY.LOWEST,
	fallback  : true,
	untouched : true
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
