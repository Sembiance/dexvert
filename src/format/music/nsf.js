"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "NES Sound File",
	website : "http://fileformats.archiveteam.org/wiki/NSF",
	ext     : [".nsf"],
	magic   : ["NES Sound File", "NES Sound Format rip"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["zxtune123"];
