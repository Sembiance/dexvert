"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Ultra Tracker Module",
	website : "http://fileformats.archiveteam.org/wiki/Ultra_Tracker",
	ext     : [".ult"],
	magic   : [/^ultratracker .*module sound data$/i, "Ultra Tracker module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["zxtune123", "awaveStudio"];
