"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "ANSI Art File",
	website        : "http://fileformats.archiveteam.org/wiki/ANSI_Art",
	ext            : [".ans"],
	forbidExtMatch : true,
	mimeType       : "text/x-ansi",
	magic          : ["ANSI escape sequence text"],
	bruteUnsafe    : true
};

exports.converterPriorty = ["ansilove", "abydosconvert"];
