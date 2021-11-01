"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Atari ST Guide Hypertext",
	ext            : [".hyp"],
	forbidExtMatch : true,
	magic          : ["Atari ST Guide Hypertext document"]
};

exports.steps = [() => ({program : "strings"})];
