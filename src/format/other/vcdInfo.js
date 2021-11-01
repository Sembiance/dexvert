"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "VCD Info File",
	ext            : [".vcd"],
	forbidExtMatch : true,
	filename       : ["info.vcd"],
	magic          : ["VCD Info File"]
};

exports.steps = [() => ({program : "strings"})];
