"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "PMG Designer",
	website : "http://fileformats.archiveteam.org/wiki/PMG_Designer",
	ext     : [".pmd"],
	magic   : ["PMG Designer"]
};

exports.converterPriorty = ["recoil2png"];
