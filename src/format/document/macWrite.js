"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "MacWrite Document",
	ext            : [".mcw", ".doc"],
	forbidExtMatch : true,
	magic          : [/^MacWrite [Dd]ocument/]
};

exports.converterPriority = ["soffice"];
