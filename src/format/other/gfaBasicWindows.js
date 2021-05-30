"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "GFA-BASIC Windows",
	ext            : [".gfw"],
	forbidExtMatch : true,
	magic          : ["GFA-BASIC Windows v3 tokenized source"]
};

exports.steps = [() => ({program : "strings"})];
