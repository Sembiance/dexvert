"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "DuneGraph",
	website : "http://fileformats.archiveteam.org/wiki/DuneGraph",
	ext     : [".dc1", ".dg1"],
	magic   : ["DuneGraph Compressed bitmap", "DuneGraph Compressed bitma"]
};

exports.converterPriority = ["recoil2png"];
