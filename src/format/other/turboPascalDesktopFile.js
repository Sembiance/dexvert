"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Turbo Pascal Desktop File",
	ext            : [".dsk"],
	forbidExtMatch : true,
	magic          : ["Turbo Pascal Desktop"]
};

exports.steps = [() => ({program : "strings"})];
