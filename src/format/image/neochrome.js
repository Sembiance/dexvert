/*
import {Format} from "../../Format.js";

export class neochrome extends Format
{
	name = "Neochrome";
	website = "http://fileformats.archiveteam.org/wiki/NEOchrome";
	ext = [".neo",".rst"];
	mimeType = "image/x-neo";
	fileSize = {".neo":32128};
	filesRequired = undefined;
	filesOptional = undefined;
	converters = ["recoil2png","nconvert","abydosconvert"]

preSteps = [null];
}
*/
/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Neochrome",
	website  : "http://fileformats.archiveteam.org/wiki/NEOchrome",
	ext      : [".neo", ".rst"],
	mimeType : "image/x-neo",
	fileSize : { ".neo" : 32128 },
	// .neo can convert on it's own but optionally uses a .rst which is useless on it's own without a corresponding .neo
	filesRequired : (state, otherFiles) => (state.input.ext.toLowerCase()===".neo" ? false : otherFiles.filter(otherFile => otherFile.toLowerCase()===`${state.input.name.toLowerCase()}.neo`)),
	filesOptional : (state, otherFiles) => (state.input.ext.toLowerCase()===".rst" ? false : otherFiles.filter(otherFile => otherFile.toLowerCase()===`${state.input.name.toLowerCase()}.rst`))
};

exports.preSteps = [state => { state.processed = state.processed || state.input.ext.toLowerCase()===".rst"; }];

exports.converterPriority = ["recoil2png", "nconvert", "abydosconvert"];

*/
