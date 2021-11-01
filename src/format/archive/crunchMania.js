"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Crunch-Mania Archive",
	website : "http://fileformats.archiveteam.org/wiki/Crunchmania",
	magic   : ["Crunch-Mania compressed data"]
};

exports.converterPriority = ["decrmtool", "ancient"];
