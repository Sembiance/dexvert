"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "PFS First Publisher",
	website : "http://fileformats.archiveteam.org/wiki/ART_(PFS:_First_Publisher)",
	ext     : [".art"]
};

exports.converterPriority = ["nconvert", "convert", "deark"];
