"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Art & Magic Module",
	website : "http://fileformats.archiveteam.org/wiki/Art_%26_Magic",
	ext     : [".aam"],
	magic   : ["Art And Magic module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123"];
