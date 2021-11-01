"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "C-Worthy Form",
	ext            : [".cwa"],
	forbidExtMatch : true,
	magic          : ["C-Worthy Form"]
};

exports.steps = [() => ({program : "strings"})];
