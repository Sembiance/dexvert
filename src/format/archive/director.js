"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Macromedia Director",
	website : "http://fileformats.archiveteam.org/wiki/Shockwave_(Director)",
	ext     : [".dxr", ".dir"],
	magic   : ["RIFX MV93 file", "Macromedia Director Protected Movie"]
};

// Haven't determined a good way to determine if it's PC or MAC file ahead of time, so we just try both
// The wrong one doesn't produce any files, so it all works out ok
exports.steps =
[
	state => ({program : "undirector", args : ["pc", state.input.filePath, state.output.dirPath]}),
	state => ({program : "undirector", args : ["mac", state.input.filePath, state.output.dirPath]})
];
