"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "MIDI Music File",
	website : "http://fileformats.archiveteam.org/wiki/MIDI",
	ext     : [".mid"],
	magic   : ["MIDI Music", "MIDI Audio", "Standard MIDI data"]
};

exports.steps =
[
	() => ({program : "timidity"}),
	(state, p) => p.util.file.findValidOutputFiles(true),
	(state, p) => p.family.validateOutputFiles
];
