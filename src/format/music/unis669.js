"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Unis 669 Module",
	ext     : [".669"],
	magic   : ["Unis 669 module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["xmp", "zxtune123", "openmpt123"];
