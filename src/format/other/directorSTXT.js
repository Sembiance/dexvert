"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Director STXT",
	ext            : [".stxt"],
	forbidExtMatch : true,
	magic          : ["Director STXT"],
	weakMagic      : true
};

exports.steps = [() => ({program : "strings"})];
