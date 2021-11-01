"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "Asylum Module",
	ext   : [".amf"],
	magic : ["Asylum Music Format module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["xmp", "openmpt123"];
