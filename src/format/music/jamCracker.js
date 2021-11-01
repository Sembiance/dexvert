"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "JamCracker Module",
	website : "http://fileformats.archiveteam.org/wiki/JAMCracker_Pro",
	ext     : [".jc"],
	magic   : [/^JamCracker [Mm]odule/]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123"];
