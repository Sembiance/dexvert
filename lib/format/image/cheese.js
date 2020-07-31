"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs");

exports.meta =
{
	name     : "Cheese",
	website  : "http://fileformats.archiveteam.org/wiki/Cheese",
	ext      : [".che"],
	mimeType : "image/x-cheese"
};

// Cheese files 'appear' to be exactly 20482 bytes in length
exports.custom = state => (fs.statSync(state.input.absolute).size===20482);

exports.converterPriorty = ["nconvert", "recoil2png", "abydosconvert"];
