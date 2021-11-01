"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Corel Plan Perfect",
	ext            : [".pln"],
	forbidExtMatch : true,
	magic          : ["Corel Plan Perfect"]
};

exports.steps = [() => ({program : "strings"})];
