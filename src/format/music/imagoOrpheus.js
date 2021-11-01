"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Imago Orpheus Module",
	website : "http://fileformats.archiveteam.org/wiki/Imago_Orpheus_module",
	ext     : [".imf"],
	magic   : ["Imago Orpheus module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["xmp", "zxtune123", "openmpt123"];
