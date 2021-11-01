"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "StoneCracker Archive",
	website : "http://fileformats.archiveteam.org/wiki/StoneCracker",
	ext     : [".stc"],
	magic   : [/^StoneCracker .*compressed$/]
};

exports.converterPriority = ["amigadepacker"];
