"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Turbo Pascal Configuration File",
	ext            : [".tp"],
	forbidExtMatch : true,
	magic          : ["Turbo Pascal configuration"]
};

exports.steps = [() => ({program : "strings"})];
