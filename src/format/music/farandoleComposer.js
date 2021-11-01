"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Farandole Composer Module",
	website : "http://fileformats.archiveteam.org/wiki/Farandole_Composer_module",
	ext     : [".far"],
	magic   : ["Farandole Composer module", "Farandole Tracker Song"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["xmp", "zxtune123", "openmpt123"];
