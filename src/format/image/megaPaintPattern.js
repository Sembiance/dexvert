"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "MegaPaint Pattern",
	website        : "http://fileformats.archiveteam.org/wiki/MegaPaint_BLD",
	ext            : [".pat"],
	forbidExtMatch : true,
	magic          : ["MegaPaint Pattern"]
};

exports.converterPriority = ["deark"];
