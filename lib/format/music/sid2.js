"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Sidmon II Module",
	website : "http://fileformats.archiveteam.org/wiki/Amiga_Module",
	ext     : [".sid2"],
	magic   : ["Sidmon II module", "Sidmon 2.0 Module sound file"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriorty = ["uade123"];
