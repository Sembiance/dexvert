"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name          : "Atari Canvas",
	ext           : [".cpt", ".hbl", ".ful"],
	// .ful is standalone. .cpt can convert on it's own, but optionally uses a .hbl. .hbl is useless without a .cpt
	filesRequired : (state, otherFiles) => ([".ful", ".cpt"].includes(state.input.ext.toLowerCase()) ? false : otherFiles.filter(otherFile => otherFile.toLowerCase()===`${state.input.name.toLowerCase()}.cpt`)),
	filesOptional : (state, otherFiles) => ([".ful", ".hbl"].includes(state.input.ext.toLowerCase()) ? false : otherFiles.filter(otherFile => otherFile.toLowerCase()===`${state.input.name.toLowerCase()}.hbl`))
};

exports.preSteps = [state => { state.processed = state.processed || state.input.ext.toLowerCase()===".hbl"; }];

exports.converterPriority = ["recoil2png"];
