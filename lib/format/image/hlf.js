"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	file = require(path.join(__dirname, "..", "..", "util", "file.js"));

exports.meta =
{
	name    : "Hires Interlace",
	website : "http://fileformats.archiveteam.org/wiki/Hires_Interlace",
	ext     : [".hlf"]
};

exports.custom = state => file.compareFileBytes(state.input.absolute, 0, Buffer.from([0x00, 0x20]));

exports.converterPriorty = ["recoil2png"];
