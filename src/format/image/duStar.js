"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Atari DU* Image",
	website  : "http://fileformats.archiveteam.org/wiki/DU*",
	ext      : [".du1", ".du2", ".duo"],
	fileSize : 113600
};

exports.converterPriorty = ["recoil2png"];
