"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Atari Works Document",
	ext            : [".stw"],
	forbidExtMatch : true,
	magic          : ["Atari Works Wordprocessor document"]
};

exports.converterPriority = ["strings"];
