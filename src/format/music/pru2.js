"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Prorunner Module",
	website : "http://fileformats.archiveteam.org/wiki/Prorunner",
	ext     : [".pru2"],
	magic   : ["Prorunner 2.0 Music"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["xmp"];
