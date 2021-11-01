"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Papyrus",
	ext            : [".pap"],
	forbidExtMatch : true,
	magic          : ["Papyrus document"]
};

exports.converterPriority = ["strings"];
