"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Future Composer Module",
	website : "http://fileformats.archiveteam.org/wiki/Future_Composer_v1.x_module",
	ext     : [".fc", ".fc13", ".fc14", ".smc", ".smod", ".bsi"],
	magic   : ["Future Composer "]	// trailing space on purpose
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123"];
