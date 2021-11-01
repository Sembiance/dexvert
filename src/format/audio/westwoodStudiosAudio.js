"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Westwood Studios Audio",
	website  : "http://fileformats.archiveteam.org/wiki/Westwood_Studios_AUD",
	ext      : [".aud"],
	magic    : ["Westwood Studios audio"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["ffmpeg"];
