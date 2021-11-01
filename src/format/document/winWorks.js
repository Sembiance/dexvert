"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "WinWorks Document",
	ext            : [".wpd"],
	forbidExtMatch : true,
	magic          : ["WinWorks text Document"]
};

exports.converterPriority = ["strings"];
