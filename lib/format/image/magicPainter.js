"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Magic Painter",
	website  : "http://fileformats.archiveteam.org/wiki/Magic_Painter",
	ext      : [".mgp"],
	magic    : ["Magic Painter bitmap"],
	filesize : 3845
};

exports.converterPriorty = ["recoil2png"];
