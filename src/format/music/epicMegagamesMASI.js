"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Epic Megagames MASI Module",
	website : "http://fileformats.archiveteam.org/wiki/Epic_Megagames_MASI",
	ext     : [".psm"],
	magic   : ["Epic Megagames MASI module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["xmp", "zxtune123", "openmpt123"];
