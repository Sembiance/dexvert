"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Impulse Tracker Module",
	website : "http://fileformats.archiveteam.org/wiki/Impulse_Tracker_module",
	ext     : [".it"],
	magic   : ["Impulse Tracker module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["xmp", "zxtune123", "openmpt123"];
