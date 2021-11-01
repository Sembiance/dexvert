"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Turbo Basic Chain module",
	ext            : [".tbc"],
	forbidExtMatch : true,
	magic          : ["Turbo Basic compiled Chain module"]
};

exports.steps = [() => ({program : "strings"})];
