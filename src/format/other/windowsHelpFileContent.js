"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Microsoft Windows Help File Content",
	ext            : [".cnt"],
	forbidExtMatch : true,
	magic          : ["Help File Contents", "MS Windows help file Content"]
};

exports.steps = [() => ({program : "strings"})];
