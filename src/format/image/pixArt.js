"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "PixArt",
	website : "http://fileformats.archiveteam.org/wiki/PixArt",
	ext     : [".pix"],
	magic   : ["PixArt bitmap"]
};

exports.converterPriority = ["recoil2png"];
