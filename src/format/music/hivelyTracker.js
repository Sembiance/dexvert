"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Hively Tracker Module",
	website : "http://fileformats.archiveteam.org/wiki/Hively_Tracker_module",
	ext     : [".hvl"],
	magic   : ["Hively Tracker module", "Hively Tracker Song"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["zxtune123"];
