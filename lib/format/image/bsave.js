"use strict";
/* eslint-disable arrow-body-style */
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "QuickBasic BSAVE Image",
	website  : "http://fileformats.archiveteam.org/wiki/BSAVE_Image",
	ext      : [".pic", ".scn", ".bsv", ".cgx"],
	magic    : ["QuickBasic BSAVE binary data"]
};

// deark can't determine what type of BSAVE format it is, so we just try em all :)
exports.steps = ["char", "cga2", "cga4", "cga16", "mcga", "wh2", "wh4", "wh16", "b256", "2col", "4col"].map(subType =>
{
	return state => ({program : "deark", args : ["-od", state.output.dirPath, "-o", `${state.input.name}_${subType}`, "-opt", `bsave:fmt=${subType}`, state.input.filePath]});
});
