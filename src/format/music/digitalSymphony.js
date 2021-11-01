"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Digital Symphony Module",
	website : "http://fileformats.archiveteam.org/wiki/Digital_Symphony_module",
	ext     : [".dsym"],
	magic   : ["Digital Symphony relocatable module", "Digital Symphony song"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["xmp", "zxtune123"];
