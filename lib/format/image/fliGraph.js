"use strict";
const XU = require("@sembiance/xu");
exports.meta =
{
	name     : "FLI Graph Image",
	website  : "http://fileformats.archiveteam.org/wiki/FLI_GraphF",
	ext      : [".bml", ".fli"],
	filesize : [17474, 17409]
};

exports.converterPriorty = ["recoil2png"];
