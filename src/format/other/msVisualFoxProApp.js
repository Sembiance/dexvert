"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "MS Visual FoxPro App",
	ext            : [".app", ".fxp"],
	forbidExtMatch : true,
	magic          : ["Generated application MS Visual FoxPro 7"]
};

exports.steps = [() => ({program : "strings"})];
