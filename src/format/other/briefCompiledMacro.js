"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Brief Compiled Macro",
	ext            : [".cm"],
	forbidExtMatch : true,
	magic          : ["Brief Compiled Macro"]
};

exports.steps = [() => ({program : "strings"})];
