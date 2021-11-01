"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Special FX Module",
	website : "http://fileformats.archiveteam.org/wiki/Special_FX",
	ext     : [".jd", ".doda"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123"];
