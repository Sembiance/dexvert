"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Atari APAC3 APP Image",
	website : "http://fileformats.archiveteam.org/wiki/Apac3_APP",
	ext     : [".app", ".aps", ".ils", ".pls"],
	magic   : ["APP raster bitmap"]
};

exports.converterPriorty = ["recoil2png"];
