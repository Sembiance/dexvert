"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Dynamic Publisher Font",
	website : "http://fileformats.archiveteam.org/wiki/Dynamic_Publisher",
	ext     : [".fnt"],
	magic   : ["Dynamic Publisher Font"]
};

exports.steps = [() => ({program : "recoil2png"})];
