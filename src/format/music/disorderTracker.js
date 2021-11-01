"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Disorder Tracker Module",
	website : "http://fileformats.archiveteam.org/wiki/669",
	ext     : [".plm"],
	magic   : ["Disorder Tracker 2 module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["zxtune123", "openmpt123"];
