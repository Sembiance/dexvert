"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Amigaguide Index",
	ext            : [".index"],
	forbidExtMatch : true,
	magic          : ["Amigaguide Index"]
};

exports.steps = [() => ({program : "strings"})];
