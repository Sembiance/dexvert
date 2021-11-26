/*
import {Format} from "../../Format.js";

export class euphony extends Format
{
	name = "EUPHONY Module";
	website = "http://fileformats.archiveteam.org/wiki/EUPHONY";
	ext = [".eup",".fmb",".pmb"];
	fileSize = {".fmb":6152};
	keepFilename = true;
	filesRequired = undefined;
	filesOptional = undefined;
	converters = ["eupplay"]

preSteps = [null];

	metaProviders = [""];
}
*/
/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	name          : "EUPHONY Module",
	website       : "http://fileformats.archiveteam.org/wiki/EUPHONY",
	ext           : [".eup", ".fmb", ".pmb"],
	fileSize      : {".fmb" : 6152},
	keepFilename  : true,
	filesRequired : (state, otherFiles) => ([".fmb", ".pmb"].includes(state.input.ext.toLowerCase()) ? false : otherFiles.filter(otherFile => [".fmb", ".pmb"].includes(path.extname(otherFile.toLowerCase())))),
	filesOptional : (state, otherFiles) => ([".fmb", ".pmb"].includes(state.input.ext.toLowerCase()) ? false : otherFiles.filter(otherFile => [".fmb", ".pmb"].includes(path.extname(otherFile.toLowerCase()))))
};

exports.preSteps = [state => { state.processed = state.processed || [".fmb", ".pmb"].includes(state.input.ext.toLowerCase()); }];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["eupplay"];

*/
