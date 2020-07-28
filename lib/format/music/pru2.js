"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Prorunner Module",
	website : "http://fileformats.archiveteam.org/wiki/Amiga_Module",
	ext     : [".pru2"],
	magic   : ["Prorunner 2.0 Music"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriorty = ["xmp"];
