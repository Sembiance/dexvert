"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name      : "Fred Fish's Product-Info",
	magic     : ["Fred Fish's Product-Info"],
	untouched : true
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
