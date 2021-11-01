"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Oktalyzer Module",
	website : "http://fileformats.archiveteam.org/wiki/Oktalyzer_module",
	ext     : [".okt", ".okta"],
	magic   : ["Oktalyzer module", "Oktalyzer Audio file"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["xmp", "zxtune123", "openmpt123", "uade123"];
