"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Borland C/C++ Project",
	ext            : [".prj"],
	forbidExtMatch : true,
	magic          : ["Borland Turbo C Project", "Borland C++"]
};

exports.steps = [() => ({program : "strings"})];
