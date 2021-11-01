"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "SidMon Module",
	website : "http://fileformats.archiveteam.org/wiki/Sidmon",
	ext     : [".sid"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123"];
