"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Tempus Word Document",
	ext            : [".twd"],
	forbidExtMatch : true,
	magic          : ["Tempus Word Document"]
};

exports.converterPriority = ["strings"];
