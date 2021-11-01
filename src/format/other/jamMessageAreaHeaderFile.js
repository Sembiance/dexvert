"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "JAM Message Area Header File",
	ext            : [".jhr"],
	forbidExtMatch : true,
	magic          : ["JAM message area header file"]
};

exports.steps = [() => ({program : "strings"})];
