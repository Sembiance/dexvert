"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Borland Turbo C Project",
	ext            : [".prj"],
	forbidExtMatch : true,
	magic          : ["Borland Turbo C Project"]
};

exports.steps = [() => ({program : "strings"})];
