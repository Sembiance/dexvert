"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "AmigaDOS Script File",
	website : "https://amigasourcecodepreservation.gitlab.io/mastering-amigados-scripts/",
	magic   : ["AmigaDOS script"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
