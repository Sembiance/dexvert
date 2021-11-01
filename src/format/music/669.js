"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Composer 669 Module",
	website : "http://fileformats.archiveteam.org/wiki/669",
	ext     : [".669"],
	magic   : ["Composer 669 module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["xmp", "zxtune123", "openmpt123"];
