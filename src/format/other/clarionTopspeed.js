"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Clarion Topspeed Data File",
	ext            : [".tps"],
	forbidExtMatch : true,
	magic          : ["Clarion Topspeed Data file"]
};

exports.steps = [() => ({program : "strings"})];
