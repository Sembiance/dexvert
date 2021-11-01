"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "dBASE Multiple Index",
	ext            : [".mdx"],
	forbidExtMatch : true,
	magic          : ["dBASE IV Multiple index", "FoxBase MDX"]
};

exports.converterPriority = ["strings"];
