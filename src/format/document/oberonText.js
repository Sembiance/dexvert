"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Oberon Text",
	ext            : [".mod"],
	forbidExtMatch : true,
	magic          : ["Oberon V4 text format"]
};

exports.converterPriority = ["strings"];
