"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name          : "Amstrad CPC Mode 5 Image",
	ext           : [".cm5", ".gfx"],
	// Both .cm5 and .gfx are required
	filesRequired : (state, otherFiles) => otherFiles.filter(otherFile => otherFile.toLowerCase()===(state.input.name.toLowerCase() + exports.meta.ext.find(ext => ext!==state.input.ext.toLowerCase())))
};

exports.preSteps = [state => { state.processed = state.processed || state.input.ext.toLowerCase()===".gfx"; }];

exports.converterPriority = ["recoil2png"];
