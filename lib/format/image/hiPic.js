"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs");

exports.meta =
{
	name     : "Hi-Pic Creator",
	website  : "http://fileformats.archiveteam.org/wiki/Hi-Pic_Creator",
	ext      : [".hpc"],
	magic    : ["Koala Paint"]	// Shares the same magic
};

// Hi-Pic files appear to be 9003 bytes in length
exports.custom = state => (fs.statSync(state.input.absolute).size===9003);

exports.converterPriorty = ["recoil2png"];
