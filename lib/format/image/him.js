"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	file = require(path.join(__dirname, "..", "..", "util", "file.js"));

exports.meta =
{
	name    : "Hires Manager",
	website : "http://fileformats.archiveteam.org/wiki/Hires_Manager",
	ext     : [".him"]
};

exports.custom = state => file.compareFileBytes(state.input.absolute, 0, Buffer.from([0x00, 0x40]));

exports.converterPriorty = ["recoil2png"];
