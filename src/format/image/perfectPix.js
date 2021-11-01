/*
import {Format} from "../../Format.js";

export class perfectPix extends Format
{
	name = "Perfect Pix";
	website = "http://fileformats.archiveteam.org/wiki/Perfect_Pix";
	ext = [".eve",".odd",".pph"];
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
	name          : "Perfect Pix",
	website       : "http://fileformats.archiveteam.org/wiki/Perfect_Pix",
	ext           : [".eve", ".odd", ".pph"],
	// All three files are required
	filesRequired : (state, otherFiles) =>
	{
		const requiredFiles = otherFiles.filter(otherFile => exports.meta.ext.filter(ext => ext!==state.input.ext.toLowerCase()).map(ext => state.input.name.toLowerCase() + ext).includes(otherFile.toLowerCase()));
		return requiredFiles.length===2 ? requiredFiles : [];
	}
};

exports.preSteps = [state => { state.processed = state.processed || [".eve", ".odd"].includes(state.input.ext.toLowerCase()); }];

exports.converterPriority = ["recoil2png"];

*/
