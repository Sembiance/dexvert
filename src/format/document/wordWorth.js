"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "WordWorth",
	magic       : ["IFF data, WOWO Wordworth document", "WordWorth document"]
};

exports.converterPriority = ["WoW", "strings"];
