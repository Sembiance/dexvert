"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "ZZ_ROUGH",
	website : "http://fileformats.archiveteam.org/wiki/ZZ_ROUGH",
	ext     : [".rgh"],
	magic : ["ZZ ROUGH bitmap"]
};

exports.converterPriority = ["recoil2png"];
