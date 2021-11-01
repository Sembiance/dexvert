"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Puma Tracker Module",
	website : "http://fileformats.archiveteam.org/wiki/Pumatracker_module",
	ext     : [".puma"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123"];
