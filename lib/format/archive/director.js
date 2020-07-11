"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Macromedia Director",
	website : "http://fileformats.archiveteam.org/wiki/Shockwave_(Director)",
	ext     : [".dxr", ".dir"],
	magic   : ["RIFX MV93 file", "Macromedia Director Protected Movie"]
};

exports.steps = (state, p) => ([p.util.program.run(p.program.undirector, {args : ["pc", state.input.filePath, state.output.dirPath]}), p.util.program.run(p.program.undirector, {args : ["mac", state.input.filePath, state.output.dirPath]})]);
