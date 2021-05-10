"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "OctaMED Module",
	website : "http://fileformats.archiveteam.org/wiki/MED",
	ext     : [".med", ".mmd1", ".mmd2", ".mmd3", ".mmd4"],
	magic   : ["OctaMED Pro music file", /OctaMED MMD\d module/, "OctaMED Music Editor module", "MED_Song", "OctaMED Soundstudio music file", "MED music file"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriorty = ["xmp", "openmpt123"];
