"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Oktalyzer Module",
	website : "http://fileformats.archiveteam.org/wiki/Amiga_Module",
	ext     : [".okt", ".okta"],
	magic   : ["Oktalyzer module", "Oktalyzer Audio file"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriorty = ["xmp"];
