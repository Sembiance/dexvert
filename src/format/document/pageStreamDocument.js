"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "PageStream Document",
	website        : "https://en.wikipedia.org/wiki/PageStream",
	ext            : [".pgs"],
	forbidExtMatch : true,
	magic          : ["PageStream Document"]
};

exports.steps = [() => ({program : "strings"})];
