"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "InstallShield Package",
	ext            : [".pkg"],
	forbidExtMatch : true,
	magic          : ["InstallShield compiled setup Package"]
};

exports.steps = [() => ({program : "strings"})];
