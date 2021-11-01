/*
import {Format} from "../../Format.js";

export class advancedArtStudio extends Format
{
	name = "Advanced Art Studio";
	website = "http://fileformats.archiveteam.org/wiki/Advanced_Art_Studio";
	ext = [".ocp",".scr",".win",".pal"];
	fileSize = {".ocp":10018};
	filesRequired = undefined;
	converters = ["recoil2png"]

preSteps = [null];
}
*/
/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name          : "Advanced Art Studio",
	website       : "http://fileformats.archiveteam.org/wiki/Advanced_Art_Studio",
	ext           : [".ocp", ".scr", ".win", ".pal"],
	fileSize      : {".ocp" : 10018},
	filesRequired : (state, otherFiles) =>
	{
		const ourExt = state.input.ext.toLowerCase();
		// .ocp is standalone
		if(ourExt===".ocp")
			return false;
		
		// .scr/.win require a corresponding .pal file
		if([".scr", ".win"].includes(ourExt))
			return otherFiles.filter(otherFile => otherFile.toLowerCase()===`${state.input.name.toLowerCase()}.pal`);
		
		// A .pal requires either a .scr or .win
		return otherFiles.filter(otherFile => [".scr", ".win"].map(ext => state.input.name.toLowerCase() + ext).includes(otherFile.toLowerCase()));
	}
};

exports.preSteps = [state => { state.processed = state.processed || state.input.ext.toLowerCase()===".pal"; }];

exports.converterPriority = ["recoil2png"];

*/
