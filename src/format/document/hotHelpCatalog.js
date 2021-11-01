"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "HotHelp Catalog",
	ext            : [".cat"],
	forbidExtMatch : true,
	magic          : ["HotHelp Catalog"]
};

exports.converterPriority = ["strings"];
