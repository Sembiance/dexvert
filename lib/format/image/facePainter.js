"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs");

exports.meta =
{
	name     : "Face Painter",
	website  : "http://fileformats.archiveteam.org/wiki/Face_Painter",
	ext      : [".fcp", ".fpt"],
	mimeType : "image/x-face-painter"
};

// Face Painter files appear to be 10004 bytes in length
exports.custom = state => (fs.statSync(state.input.absolute).size===10004);

exports.converterPriorty = ["abydosconvert", "recoil2png"];
