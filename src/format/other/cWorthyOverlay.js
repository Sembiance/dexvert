"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "C-Worthy Machine Overlay",
	ext            : [".ovl"],
	forbidExtMatch : true,
	magic          : ["C-Worthy Machine Dependant Overlay"]
};

exports.steps = [() => ({program : "strings"})];
