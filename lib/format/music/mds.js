"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	name    : "RIFF MIDS File",
	website : "http://fileformats.archiveteam.org/wiki/RIFF_MIDS",
	ext     : [".mds"],
	magic   : ["RIFF MIDS file"]
};

exports.steps =
[
	() => ({program : "midistar2mid"}),
	() => (state, p, cb) => { state.input.filePath = path.join(state.output.dirPath, `${state.input.name}.mid`); setImmediate(cb); },
	() => ({program : "timidity"}),
	(state, p) => p.util.file.findValidOutputFiles(true),
	(state, p) => p.family.validateOutputFiles
];
