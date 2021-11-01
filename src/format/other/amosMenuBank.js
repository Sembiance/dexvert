"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "AMOS Menu Bank",
	ext            : [".abk"],
	forbidExtMatch : true,
	magic          : ["AMOS Menu Bank"]
};

exports.steps = [() => ({program : "strings"})];
