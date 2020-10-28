"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	C = require(path.join(__dirname, "..", "..", "C.js"));

exports.meta =
{
	name    : "Nero CD Image",
	website : "http://fileformats.archiveteam.org/wiki/NRG",
	ext     : [".nrg"],
	magic   : ["Nero CD image"],
	priority : C.PRIORITY.TOP	// NRG is often mis-identified as ISO
};

exports.steps =
[
	() => ({program : "nrg2iso"}),
	state => ({program : "uniso", argsd : [path.join(state.output.dirPath, "outfile.iso")]}),
	(state, p) => p.util.file.unlink(path.join(state.output.absolute, "outfile.iso"))
];
