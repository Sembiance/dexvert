"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Turbo Pascal Overlay",
	ext            : [".ovr"],
	forbidExtMatch : true,
	magic          : ["Turbo Pascal Overlay"]
};

exports.steps = [() => ({program : "strings"})];
