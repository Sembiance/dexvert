"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Doodle Atari",
	website  : "http://fileformats.archiveteam.org/wiki/Doodle_(Atari)",
	ext      : [".doo"],
	fileSize : 32000
};

exports.converterPriorty = ["deark", "recoil2png"];
