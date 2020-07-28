"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Star Tracker Module",
	website : "http://fileformats.archiveteam.org/wiki/Amiga_Module",
	ext     : [".mod"],
	magic   : [/^StarTrekker.* module$/, /Startracker module sound data/]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriorty = ["xmp"];
