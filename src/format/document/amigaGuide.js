"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name          : "Amigaguide Document",
	website       : "http://fileformats.archiveteam.org/wiki/AmigaGuide",
	ext           : [".guide"],
	magic         : ["Amigaguide hypertext document", "AmigaGuide file"],
	keepFilename  : true,
	filesOptional : (state, otherFiles, otherDirs) => ([...otherFiles, ...otherDirs])	// Amiga Guides reference other guides and directories, so include symlinks to everything else
};

exports.steps = [() => ({program : "grotag"})];
