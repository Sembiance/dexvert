"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Turbo Debugger Configuration",
	ext            : [".td", ".td2"],
	forbidExtMatch : true,
	magic          : ["Turbo Debugger configuration"]
};

exports.steps = [() => ({program : "strings"})];
