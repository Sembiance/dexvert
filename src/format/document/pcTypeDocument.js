"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "PC-Type Document",
	ext            : [".pct"],
	forbidExtMatch : true,
	magic          : ["PC-Type document"]
};

exports.converterPriority = ["strings"];
