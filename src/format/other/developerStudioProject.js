"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Microsoft Developer Studio Project",
	ext            : [".mdp"],
	forbidExtMatch : true,
	magic          : ["Microsoft Developer Studio Project"]
};

exports.steps = [() => ({program : "strings"})];
