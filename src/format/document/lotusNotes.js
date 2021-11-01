"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Lotus Notes Database",
	ext            : [".nsf"],
	forbidExtMatch : true,
	magic          : ["Lotus Notes database"]
};

exports.converterPriority = ["strings"];
