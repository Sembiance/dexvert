"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Novell DOS Client Message",
	ext            : [".msg"],
	forbidExtMatch : true,
	magic          : ["Novell DOS client message"]
};

exports.converterPriority = ["strings"];
