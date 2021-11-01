"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name      : "SYMDEF File",
	ext       : [".symdef"],
	magic     : [/^data$/],
	weakMagic : true
};

exports.steps = [() => ({program : "strings"})];
