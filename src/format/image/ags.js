"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Atari Graphics Studio",
	website : "http://g2f.atari8.info/",
	ext     : [".ags"],
	magic   : ["Atari Graphics Studio bitmap"]
};

exports.converterPriority = ["recoil2png"];
