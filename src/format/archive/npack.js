"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "NPack Archive",
	website        : "http://fileformats.archiveteam.org/wiki/NPack",
	ext            : [".$"],
	forbidExtMatch : true,
	magic          : ["NPack archive data"]
};

exports.converterPriority = ["npack"];
