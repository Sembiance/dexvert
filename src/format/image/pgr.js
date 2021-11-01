"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name      : "PowerGraphics",
	website   : "http://fileformats.archiveteam.org/wiki/PowerGraphics",
	ext       : [".pgr"],
	magic     : ["PowerGraphics bitmap"]
};

exports.converterPriority = ["recoil2png"];
