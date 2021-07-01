"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "QuickBASIC Tokenized Source",
	ext            : [".bas"],
	forbidExtMatch : true,
	magic          : ["Microsoft QuickBASIC 4.5 tokenized source"]
};

exports.steps = [() => ({program : "strings"})];
