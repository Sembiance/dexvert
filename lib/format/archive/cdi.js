"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	name          : "Compact Disc-Interactive",
	website       : "http://fileformats.archiveteam.org/wiki/Cd-i",
	ext           : [".bin"],
	magic         : ["CD-I disk image"],
	keepFilename  : true,
	filesRequired : (state, otherFiles) => otherFiles.filter(otherFile => otherFile.toLowerCase()===`${state.input.name.toLowerCase()}.cue`)
};

// IsoBuster command line options: https://www.isobuster.com/help/use_of_command_line_parameters

exports.steps =
[
	(state, p) => p.util.wine.run({cmd : "IsoBuster/IsoBuster.exe", args : [`/ef:z:${path.join(state.cwd, state.output.dirPath).replaceAll("/", "\\")}`, path.join(state.cwd, state.input.filePath).replaceAll("/", "\\"), "/c"], timeout : XU.MINUTE*15})
];
