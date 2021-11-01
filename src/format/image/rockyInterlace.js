"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Rocky Interlace Picture",
	website : "http://fileformats.archiveteam.org/wiki/Rocky_Interlace_Picture",
	ext     : [".rip"],
	magic   : ["Rocky Interlace Picture bitmap"]
};

exports.converterPriority = ["recoil2png"];
