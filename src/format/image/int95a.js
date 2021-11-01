"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "INT95a",
	website : "http://fileformats.archiveteam.org/wiki/INT95a",
	ext     : [".int"],
	magic   : ["Atari INT95a bitmap"]
};

exports.converterPriority = ["recoil2png"];
