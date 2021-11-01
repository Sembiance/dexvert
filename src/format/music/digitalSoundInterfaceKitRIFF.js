"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "Digital Sound Interface Kit RIFF Module",
	ext   : [".dsm"],
	magic : ["Digital Sound Interface Kit (RIFF) module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["zxtune123", "openmpt123"];
