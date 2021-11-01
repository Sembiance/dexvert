"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "FunkTracker Module",
	website : "http://fileformats.archiveteam.org/wiki/FunkTracker_module",
	ext     : [".fnk"],
	magic   : ["FunkTracker module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["xmp", "zxtune123"];
