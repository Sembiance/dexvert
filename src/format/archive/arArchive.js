"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "AR Archive",
	website : "http://fileformats.archiveteam.org/wiki/AR",
	ext     : [".a", ".lib"],
	magic   : ["current ar archive", "ar archive"]
};

exports.converterPriority = ["deark", "ar"];
