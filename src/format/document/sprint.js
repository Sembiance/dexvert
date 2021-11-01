"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Sprint Document",
	ext            : [".spr"],
	forbidExtMatch : true,
	magic          : ["Sprint document"]
};

exports.converterPriority = ["strings"];
