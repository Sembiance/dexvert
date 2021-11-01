"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "ITS International Module",
	ext            : [".int"],
	forbidExtMatch : true,
	magic          : ["ITS international module"]
};

exports.converterPriority = ["strings"];
