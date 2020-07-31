"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs");

exports.meta =
{
	name     : "Atari CAD",
	website  : "http://fileformats.archiveteam.org/wiki/AtariCAD",
	ext      : [".drg"],
	mimeType : "image/x-atari-cad"
};

// Atari CAD files are exactly 6400 bytes long
exports.custom = state => (fs.statSync(state.input.absolute).size===6400);

exports.converterPriorty = ["recoil2png", "abydosconvert"];
