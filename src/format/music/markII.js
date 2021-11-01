"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "Mark II Sound-System Module",
	ext   : [".mk2", ".mkii"],
	magic : ["Mark II Sound-System module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123"];
