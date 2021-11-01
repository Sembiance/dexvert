"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Wordsearch Mania! Puzzle",
	ext            : [".wsp"],
	forbidExtMatch : true,
	magic          : ["Wordsearch Mania! Puzzle"]
};

exports.steps = [() => ({program : "strings"})];
