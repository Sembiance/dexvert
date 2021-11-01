"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "NoteWorthy Composure",
	ext            : [".nw"],
	forbidExtMatch : true,
	magic          : ["NoteWorthy song"]
};

exports.steps = [() => ({program : "strings"})];
