"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name          : "Technicolor Dream",
	website       : "http://fileformats.archiveteam.org/wiki/Technicolor_Dream",
	ext           : [".lum", ".col"],
	// .lum can convert on it's own but optionally uses a .col which is useless on it's own without a corresponding .lum
	filesRequired : (state, otherFiles) => (state.input.ext.toLowerCase()===".lum" ? false : otherFiles.filter(otherFile => otherFile.toLowerCase()===`${state.input.name.toLowerCase()}.lum`)),
	filesOptional : (state, otherFiles) => (state.input.ext.toLowerCase()===".col" ? false : otherFiles.filter(otherFile => otherFile.toLowerCase()===`${state.input.name.toLowerCase()}.col`))
};

exports.preSteps = [state => { state.processed = state.processed || state.input.ext.toLowerCase()===".col"; }];

exports.converterPriority = ["recoil2png"];
