"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Turbo C Context File",
	ext            : [".dsk"],
	forbidExtMatch : true,
	magic          : ["Turbo C Context"]
};

exports.steps = [() => ({program : "strings"})];
