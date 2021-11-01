"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "MSVC Resource File",
	ext            : [".res"],
	forbidExtMatch : true,
	magic          : ["MSVC .res", "Windows compiled resource"]
};

exports.steps = [() => ({program : "strings"})];
