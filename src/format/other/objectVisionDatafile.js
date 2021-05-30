"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "ObjectVision Datafile",
	ext            : [".ovd"],
	forbidExtMatch : true,
	magic          : ["ObjectVision Datafile"]
};

exports.steps = [() => ({program : "strings"})];
