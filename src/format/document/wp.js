"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "WordPerfect document",
	website        : "http://fileformats.archiveteam.org/wiki/WordPerfect",
	ext            : [".wp", ".wpd", ".wp4", ".wp5", ".wp6", ".wp7", ".doc"],
	forbidExtMatch : true,
	magic          : [/^WordPerfect.* [Dd]ocument/],
	unsafe         : true
};

exports.converterPriority = ["soffice", "fileMerlin"];
