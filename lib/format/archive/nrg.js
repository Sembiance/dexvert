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
	(state, p) => ({program : "uniso", args : p.program.uniso.args(state, p, path.join(state.cwd, "outfile.iso"))})
];

