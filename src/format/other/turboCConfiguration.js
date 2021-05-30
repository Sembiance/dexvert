"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Turbo C Configuration",
	ext            : [".tc"],
	forbidExtMatch : true,
	magic          : ["Turbo C Configuration"]
};

exports.steps = [() => ({program : "strings"})];
