"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "AMOS Samples Bank",
	website : "http://fileformats.archiveteam.org/wiki/AMOS_Memory_Bank#AMOS_Samples_Bank",
	ext     : [".abk"],
	magic   : ["AMOS Samples Bank"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["amosbank"];
