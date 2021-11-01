"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "OS/2 INI File",
	ext            : [".ini"],
	forbidExtMatch : true,
	magic          : ["OS/2 INI"],
	notes          : "Just usings `strings` seems to do a pretty good at extracting the contents. Additional tools to process these files: https://www.os2site.com/sw/util/ini/index.html"
};

exports.steps = [() => ({program : "strings"})];
