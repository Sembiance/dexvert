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
