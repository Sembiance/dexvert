"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "AMOS Music Bank",
	website : "http://fileformats.archiveteam.org/wiki/AMOS_Music_Bank",
	ext     : [".abk"],
	magic   : ["AMOS Music Bank", /^AMOS Basic memory bank.* type Music$/]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["xmp"];
