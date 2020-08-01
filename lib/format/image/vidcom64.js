"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs");

exports.meta =
{
	name     : "Vidcom 64",
	website  : "http://fileformats.archiveteam.org/wiki/Vidcom_64",
	ext      : [".vid"],
	mimeType : "image/x-vidcom-64",
	magic    : ["Drazpaint (C64) bitmap"]	// Shares same magic identifier as Drazpaint
};

// Vidcom 64 files appear to be 10050 bytes in length
exports.custom = state => (fs.statSync(state.input.absolute).size===10050);

exports.converterPriorty = ["nconvert", "recoil2png", "abydosconvert"];
