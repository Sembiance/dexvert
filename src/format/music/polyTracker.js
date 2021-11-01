"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Poly Tracker Module",
	website : "http://fileformats.archiveteam.org/wiki/Poly_Tracker_module",
	ext     : [".ptm"],
	magic   : ["Poly Tracker PTM Module", "Poly Tracker Module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["zxtune123"];
