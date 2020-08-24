"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	name    : "Extended MIDI",
	website : "http://fileformats.archiveteam.org/wiki/XMI_(Extended_MIDI)",
	ext     : [".xmi"],
	magic   : ["Extended MIDI"]
};

exports.steps =
[
	() => ({program : "midistar2mid"}),
	(state, p) => ({program : "timidity", args : p.program.timidity.args(state, p, path.join(state.output.dirPath, `${state.input.name}.mid`))}),
	(state, p) => p.util.file.findValidOutputFiles(true),
	(state, p) => p.family.validateOutputFiles
];
