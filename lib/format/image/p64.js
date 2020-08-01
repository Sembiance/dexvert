"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs");

exports.meta =
{
	name     : "Picasso 64",
	website  : "http://fileformats.archiveteam.org/wiki/Picasso_64",
	ext      : [".p64"],
	mimeType : "image/x-picasso-64",
	magic    : ["Picasso 64 Image"]
};

// Picasso 64 files are 10050 bytes in length
exports.custom = state => (fs.statSync(state.input.absolute).size===10050);

exports.converterPriorty = ["abydosconvert", "nconvert", "recoil2png"];
