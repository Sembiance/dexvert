"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Home Accounts",
	ext            : [".ha", ".ha2"],
	forbidExtMatch : true,
	magic          : ["Home Accounts account"]
};

exports.converterPriority = ["strings"];
