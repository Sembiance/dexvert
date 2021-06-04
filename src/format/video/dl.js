"use strict";
const XU = require("@sembiance/xu"),
	file = require("../../util/file.js");

exports.meta =
{
	name    : "DL Video",
	website : "http://fileformats.archiveteam.org/wiki/DL",
	ext     : [".dl"],
	notes   : XU.trim`
		Could not find a modern viewer/extractor (rumor has it Graphics Converter for MacOS X supports this, but haven't tried.
		I could spin up the DOS DL_VIEWER.EXE program and record the X11 output as video but can't currently identify DL files safely.
		Source code for an old DOS viewer is here: https://github.com/lucadegregorio/dl-viewer
		Could examine said source code to reverse engineer the format and build a converter. Maybe some day.`
};

// dl files will start with 0x03, 0x02 or 0x01
exports.idCheck = state => file.compareFileBytes(state.input.absolute, 0, [Buffer.from([0x03]), Buffer.from([0x02]), Buffer.from([0x01])]);

exports.steps = [() => ({program : "deark", flags : {dearkModule : "dlmaker", dearkJoinFrames : true}})];
