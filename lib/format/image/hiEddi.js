"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs");

exports.meta =
{
	name     : "Hi-Eddi",
	website  : "http://fileformats.archiveteam.org/wiki/Hi-Eddit",
	ext      : [".hed"],
	mimeType : "image/x-hi-eddi"
};

// Face Painter files appear to be 9218 bytes in length
exports.custom = state => (fs.statSync(state.input.absolute).size===9218);

exports.converterPriorty = ["abydosconvert", "nconvert"];
