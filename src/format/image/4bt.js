"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "GoDot 4Bit Image",
	website        : "http://fileformats.archiveteam.org/wiki/GoDot",
	ext            : [".4bt", ".clp"],
	forbidExtMatch : [".clp"],
	magic          : ["GoDot 4-bit graphics bitmap"]
};

exports.converterPriority = ["recoil2png", "nconvert", "view64"];
