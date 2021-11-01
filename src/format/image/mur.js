"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name          : "C.O.L.R. Object Editor",
	website       : "http://fileformats.archiveteam.org/wiki/C.O.L.R._Object_Editor",
	ext           : [".mur", ".pal"],
	// Both .mur and .pal are required
	filesRequired : (state, otherFiles) => otherFiles.filter(otherFile => otherFile.toLowerCase()===(state.input.name.toLowerCase() + exports.meta.ext.find(ext => ext!==state.input.ext.toLowerCase())))
};

exports.preSteps = [state => { state.processed = state.processed || state.input.ext.toLowerCase()===".pal"; }];

exports.converterPriority = ["recoil2png"];
