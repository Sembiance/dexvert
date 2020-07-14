"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name             : "DigiTrekker",
	website          : "http://fileformats.archiveteam.org/wiki/DigiTrekker_module",
	ext              : [".dtm"],
	magic            : ["DigiTrekker DTM Module", "Digitrekker module"],
	unsupported      : true,
	unsupportedNotes : "Couldn't locate a player or converter. Tried milkytracker, but it wouldn't play it."
};
