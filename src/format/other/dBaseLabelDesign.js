"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "dBase Label Design",
	ext            : [".lbl"],
	forbidExtMatch : true,
	magic          : ["dBASE IV Label design"]
};

exports.steps = [() => ({program : "strings"})];
