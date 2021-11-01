"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "COKE",
	website : "http://fileformats.archiveteam.org/wiki/COKE_(Atari_Falcon)",
	ext     : [".tg1"],
	magic   : ["COKE format bitmap"]
};

exports.converterPriority = ["recoil2png"];
