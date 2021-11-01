"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "MicroHelp",
	ext            : [".slb"],
	forbidExtMatch : true,
	magic          : ["MicroHelp Library"]
};

exports.converterPriority = ["strings"];
