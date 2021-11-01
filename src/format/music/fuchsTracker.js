"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Fuchs Tracker module",
	website : "http://fileformats.archiveteam.org/wiki/Fuchs_Tracker",
	ext     : [".fuchs", ".ft"],
	magic   : ["Fuchs Tracker module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["xmp"];
