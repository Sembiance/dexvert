"use strict";
const XU = require("@sembiance/xu"),
	file = require("../../util/file.js");

exports.meta =
{
	name    : "Hires Manager",
	website : "http://fileformats.archiveteam.org/wiki/Hires_Manager",
	ext     : [".him"]
};

exports.idCheck = state => file.compareFileBytes(state.input.absolute, 0, Buffer.from([0x00, 0x40]));

exports.converterPriority = ["recoil2png", "view64"];
