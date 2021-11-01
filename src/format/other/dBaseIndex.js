"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "dBase Index",
	ext            : [".mdx"],
	forbidExtMatch : true,
	magic          : ["dBASE IV Multiple index"]
};

exports.steps = [() => ({program : "strings"})];
