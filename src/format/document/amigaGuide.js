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

// Grotag is best because it'll have access to the 'otherFiles' and 'otherDirs'
// If that fails though, guideml will at least process the text content in this particular guide file
// Finally we fall back to strings
exports.converterPriority = ["grotag", "guideml", "strings"];
