"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Borland Reflex Database",
	ext            : [".rxd"],
	forbidExtMatch : true,
	magic          : ["Borland Reflex Database"]
};

exports.steps = [() => ({program : "strings"})];
