"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Atari Works Spreadsheet",
	ext            : [".sts"],
	forbidExtMatch : true,
	magic          : ["Atari Works Spreadsheet"]
};

exports.converterPriority = ["strings"];
