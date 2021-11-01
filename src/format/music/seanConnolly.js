"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Sean Connolly Module",
	website : "http://fileformats.archiveteam.org/wiki/Sean_Connolly",
	ext     : [".scn"],
	magic   : ["Sean Connolly module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123"];
