"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "MIG",
	website : "http://fileformats.archiveteam.org/wiki/MIG",
	ext     : [".mig"],
	magic   : ["MSX compressed Image bitmap"]
};

exports.converterPriority = ["recoil2png"];
