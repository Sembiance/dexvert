"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Amiga Catalog Translation file",
	ext            : [".ct"],
	forbidExtMatch : true,
	magic          : ["catalog translation"]
};

exports.converterPriority = ["strings"];
