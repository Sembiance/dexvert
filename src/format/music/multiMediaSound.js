"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "MultiMedia Sound Module",
	ext   : [".mms"],
	magic : ["MultiMedia Sound module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123", "zxtune123", "openmpt123"];
