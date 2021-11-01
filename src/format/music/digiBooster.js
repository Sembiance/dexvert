"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "DigiBooster Module",
	website : "http://fileformats.archiveteam.org/wiki/DigiBooster_v1.x_module",
	ext     : [".digi", ".dbm"],
	magic   : ["DIGIBooster module", "DIGI Booster module", "DIGI Booster Pro Module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["zxtune123", "uade123"];
