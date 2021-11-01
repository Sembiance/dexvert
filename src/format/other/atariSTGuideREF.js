"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Atari ST Guide REF Links",
	ext            : [".ref"],
	forbidExtMatch : true,
	magic          : ["Atari ST Guide ref links"]
};

exports.steps = [() => ({program : "strings"})];
