"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Superbase Program",
	ext            : [".sbp"],
	forbidExtMatch : true,
	magic          : ["Superbase Program"]
};

exports.converterPriorty = ["strings"];
