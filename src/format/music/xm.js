"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Extended Module",
	website : "http://fileformats.archiveteam.org/wiki/XM",
	ext     : [".xm"],
	magic   : ["Fasttracker II module sound data", "FastTracker 2 eXtended Module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["xmp", "zxtune123"];
