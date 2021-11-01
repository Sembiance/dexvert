"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Dynamic Publisher Screen",
	website : "http://fileformats.archiveteam.org/wiki/Dynamic_Publisher",
	ext     : [".pct"],
	magic   : ["Dynamic Publisher Picture/Screen"]
};

exports.converterPriority = ["recoil2png"];
