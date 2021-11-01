"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Microsoft QuickPascal Unit",
	ext            : [".qpu"],
	forbidExtMatch : true,
	magic          : ["Microsoft QuickPascal Unit"]
};

exports.steps = [() => ({program : "strings"})];
