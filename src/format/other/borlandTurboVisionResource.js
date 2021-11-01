"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Borland Turbo Vision Resource",
	ext            : [".res", ".tvr"],
	forbidExtMatch : true,
	magic          : ["Borland Turbo Vision Resource"]
};

exports.steps = [() => ({program : "strings"})];
