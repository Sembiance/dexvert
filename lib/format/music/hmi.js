"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	name    : "Human Machine Interfaces MIDI Format",
	website : "http://fileformats.archiveteam.org/wiki/HMI",
	ext     : [".hmi", ".hmp"],
	magic   : ["Human Machine Interfaces MIDI Format"]
};

exports.steps =
[
	() => ({program : "midistar2mid"}),
	() => (state, p, cb) => { state.input.filePath = path.join(state.output.dirPath, `${state.input.name}.mid`); setImmediate(cb); },
	() => ({program : "timidity"}),
	(state, p) => p.util.file.findValidOutputFiles(true),
	(state, p) => p.family.validateOutputFiles
];
