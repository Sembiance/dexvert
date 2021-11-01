"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Asymetrix ToolBook File",
	ext            : [".tbk"],
	forbidExtMatch : true,
	magic          : ["Asymetrix ToolBook"]
};

exports.steps = [() => ({program : "strings"})];
