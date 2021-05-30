"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Windows Program Group",
	ext            : [".grp"],
	forbidExtMatch : true,
	magic          : ["Windows Program Manager Group", "Windows 3.x .GRP file"]
};

exports.steps = [() => ({program : "strings"})];
