"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Dart Desktop",
	ext            : [".dsk"],
	forbidExtMatch : true,
	magic          : ["Dart Desktop"]
};

exports.steps = [() => ({program : "strings"})];
