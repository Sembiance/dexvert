"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "SidMon II Module",
	website : "http://fileformats.archiveteam.org/wiki/Sidmon",
	ext     : [".sid2"],
	magic   : ["Sidmon II module", "Sidmon 2.0 Module sound file"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123"];
