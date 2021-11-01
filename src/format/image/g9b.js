"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "GFX9k G9B",
	website : "http://fileformats.archiveteam.org/wiki/G9B",
	ext     : [".g9b"],
	magic   : ["G9B graphics format bitmap"]
};

exports.converterPriority = ["recoil2png"];
