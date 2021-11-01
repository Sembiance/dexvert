"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "InstallShield Script",
	ext            : [".ins"],
	forbidExtMatch : true,
	magic          : ["InstallShield Script"]
};

exports.steps = [() => ({program : "strings"})];
