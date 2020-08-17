"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	file = require(path.join(__dirname, "..", "..", "util", "file.js"));

exports.meta =
{
	name     : "Gunpaint",
	website  : "http://fileformats.archiveteam.org/wiki/Gunpaint",
	ext      : [".gun", ".ifl"],
	filesize : [33603]
};

exports.idCheck = state => file.compareFileBytes(state.input.absolute, 0, Buffer.from([0x00, 0x40]));

exports.converterPriorty = ["recoil2png"];
