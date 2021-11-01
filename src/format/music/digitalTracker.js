"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Digital Tracker Module",
	website : "http://fileformats.archiveteam.org/wiki/Digital_Tracker_module",
	ext     : [".dtm"],
	magic   : ["Digital Tracker 1.9 module", /^Digital Tracker \d-channel module$/]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["xmp", "zxtune123", "openmpt123"];
