"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "Sam Coupe SNG Module",
	ext   : [".sng"],
	notes : "Not all files converted, such as tetris.sng and shanhai.sng"
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["zxtune123"];
