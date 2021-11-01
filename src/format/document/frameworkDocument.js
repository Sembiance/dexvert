"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "FrameworkDocument",
	ext            : [".fw2", ".fw3"],
	forbidExtMatch : true,
	magic          : [/^Framework.* document/]
};

exports.converterPriority = ["strings"];
