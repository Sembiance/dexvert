"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Velvet Studio Module",
	website : "http://fileformats.archiveteam.org/wiki/Velvet_Studio",
	ext     : [".ams"],
	magic   : ["Velvet Studio AMS Module", "Velvet Studio Advanced Module System module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["zxtune123", "openmpt123"];
