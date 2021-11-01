"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Text Plus Document",
	ext            : [".txp"],
	forbidExtMatch : true,
	magic          : ["Text Plus document"]
};

exports.converterPriority = ["strings"];
