import {Format} from "../../Format.js";

export class cdi extends Format
{
	name         = "Compact Disc-Interactive";
	website      = "http://fileformats.archiveteam.org/wiki/Cd-i";
	ext          = [".bin"];
	magic        = ["CD-I disk image"];
	keepFilename = true;
	auxFiles     = (input, otherFiles) => otherFiles.filter(file => file.base.toLowerCase()===`${input.name.toLowerCase()}.cue`);
	converters   = ["IsoBuster"]
}

/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name          : "Compact Disc-Interactive",
	website       : "http://fileformats.archiveteam.org/wiki/Cd-i",
	ext           : [".bin"],
	magic         : ["CD-I disk image"],
	keepFilename  : true,
	filesRequired : (state, otherFiles) => otherFiles.filter(otherFile => otherFile.toLowerCase()===`${state.input.name.toLowerCase()}.cue`)
};

exports.converterPriority = ["IsoBuster"];

*/
