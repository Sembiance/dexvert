"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Help Librarian Help File",
	website        : "http://fileformats.archiveteam.org/wiki/Help_Librarian",
	ext            : [".hlp"],
	forbidExtMatch : true,
	magic          : ["C-Worthy Help Librarian Data"]
};

exports.converterPriority = ["strings"];
