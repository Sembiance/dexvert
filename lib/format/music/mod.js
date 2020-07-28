"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Protracker Module",
	website : "http://fileformats.archiveteam.org/wiki/Amiga_Module",
	ext     : [".mod"],
	magic   : [/.*Protracker module/]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriorty = ["xmp"];

