"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Telemate Compiled Script",
	ext            : [".tms"],
	forbidExtMatch : true,
	magic          : ["Telemate compiled script"]
};

exports.steps = [() => ({program : "strings"})];
