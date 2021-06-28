"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Star Tracker Module",
	website : "http://fileformats.archiveteam.org/wiki/StarTrekker_/_Star_Tracker_module",
	ext     : [".mod"],
	magic   : [/^StarTrekker.* module$/, /Startracker module sound data/]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriorty = ["xmp", "zxtune123"];
