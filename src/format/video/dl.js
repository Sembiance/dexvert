"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "DL Video",
	website     : "http://fileformats.archiveteam.org/wiki/DL",
	ext         : [".dl"],
	unsupported : true,
	notes       : XU.trim`
		Could not find a modern viewer/extractor (rumor has it Graphics Converter for MacOS X supports this, but haven't tried.
		I could spin up the DOS DL_VIEWER.EXE program and record the X11 output as video but can't currently identify DL files safely.
		Source code for an old DOS viewer is here: https://github.com/lucadegregorio/dl-viewer
		Could examine said source code to reverse engineer the format and build a converter. Maybe some day.`
};
