"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "General Digital Music",
	website : "http://fileformats.archiveteam.org/wiki/General_Digital_Music_module",
	ext     : [".gdm"],
	magic   : ["General Digital Music"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["xmp", "zxtune123", "openmpt123"];
