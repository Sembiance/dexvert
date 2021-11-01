"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Atari Works Database",
	ext            : [".std"],
	forbidExtMatch : true,
	magic          : ["Atari Works Database"]
};

exports.converterPriority = ["strings"];
