"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Ludek Maker",
	website : "http://fileformats.archiveteam.org/wiki/Ludek_Maker",
	ext     : [".ldm"],
	magic   : ["Ludek Maker bitmap"]
};

exports.converterPriority = ["recoil2png"];
