"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name      : "AMOS Source Code",
	ext       : [".amossourcecode"],
	untouched : true
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
