"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "SPC",
	website : "http://fileformats.archiveteam.org/wiki/SPC_(Audio)",
	ext     : [".spc"],
	magic   : ["SNES SPC700 sound file", "Super Famicon/Super NES audio dump"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["zxtune123"];
