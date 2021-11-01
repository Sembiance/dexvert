"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Hewlett-Packard Graphics Language",
	website : "http://fileformats.archiveteam.org/wiki/HPGL",
	ext     : [".hpgl"],
	magic   : ["Hewlett-Packard Graphics Language"]
};

exports.converterPriority = ["totalCADConverterX"];
