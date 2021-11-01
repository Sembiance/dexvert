"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "OS/2 Message File",
	website        : "http://fileformats.archiveteam.org/wiki/MSG_(OS/2)",
	ext            : [".msg"],
	forbidExtMatch : true,
	magic          : [/^OS\/2 help [Mm]essage/]
};

exports.converterPriority = ["strings"];
