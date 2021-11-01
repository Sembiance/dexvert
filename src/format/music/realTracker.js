"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Real Tracker Module",
	website : "http://fileformats.archiveteam.org/wiki/Real_Tracker_module",
	ext     : [".rtm"],
	magic   : ["Real Tracker module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["xmp", "zxtune123"];
