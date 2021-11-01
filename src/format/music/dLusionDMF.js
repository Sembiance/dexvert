"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "D-Lusion Music Format",
	website : "http://fileformats.archiveteam.org/wiki/DMF",
	ext     : [".dmf"],
	magic   : ["Xtracker DMF Module", "D-Lusion Music Format module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["zxtune123", "openmpt123"];
