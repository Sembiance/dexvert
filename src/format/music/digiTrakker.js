"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "DigiTrakker Module",
	website : "http://fileformats.archiveteam.org/wiki/Digitrakker_module",
	ext     : [".mdl"],
	magic   : ["DigiTrakker MDL Module", "Digitrakker module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["xmp", "zxtune123", "openmpt123"];
