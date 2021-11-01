"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "IBM PC Overlay",
	ext            : [".ovl"],
	forbidExtMatch : true,
	magic          : ["IBM PC Overlay"]
};

exports.steps = [() => ({program : "strings"})];
