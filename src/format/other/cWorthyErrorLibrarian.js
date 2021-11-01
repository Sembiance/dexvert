"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "C-Worthy Error Librarian Data",
	ext            : [".dat"],
	forbidExtMatch : true,
	magic          : ["C-Worthy Error Librarian Data"]
};

exports.steps = [() => ({program : "strings"})];
