"use strict";
const XU = require("@sembiance/xu"),
	file = require("../../util/file.js");

exports.meta =
{
	name    : "Hires Interlace",
	website : "http://fileformats.archiveteam.org/wiki/Hires_Interlace",
	ext     : [".hlf"]
};

exports.idCheck = state => file.compareFileBytes(state.input.absolute, 0, Buffer.from([0x00, 0x20]));

exports.converterPriority = ["recoil2png"];
