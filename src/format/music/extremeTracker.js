"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Extreme's Tracker Module",
	website : "http://fileformats.archiveteam.org/wiki/Extreme%27s_Tracker_module",
	ext     : [".ams"],
	magic   : ["Extreme Tracker AMS Module", "Extreme's Tracker module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["zxtune123"];
