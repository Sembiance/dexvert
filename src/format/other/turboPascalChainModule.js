"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Turbo Pascal Chain module",
	ext            : [".chn"],
	forbidExtMatch : true,
	magic          : ["Turbo Pascal 2.0 Chain module"]
};

exports.steps = [() => ({program : "strings"})];
