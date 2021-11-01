"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "MultiTracker Module",
	website : "http://fileformats.archiveteam.org/wiki/Multi_Track_Module",
	ext     : [".mtm"],
	magic   : [/^Multi[Tt]racker /]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["zxtune123"];
