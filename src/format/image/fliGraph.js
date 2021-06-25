"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "FLI Graph Image",
	website        : "http://fileformats.archiveteam.org/wiki/FLI_Graph",
	ext            : [".bml", ".fli"],
	forbidExtMatch : true,
	fileSize       : {".bml" : 17474, ".fli" : 17409}
};

exports.converterPriorty = ["recoil2png", "view64"];
