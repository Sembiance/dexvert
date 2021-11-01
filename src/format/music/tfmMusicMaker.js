"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "TFM Music Maker Module",
	ext   : [".tfe"],
	magic : ["TFM Music Maker music"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["zxtune123"];
