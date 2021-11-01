"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Visual Basic Project",
	website        : "http://fileformats.archiveteam.org/wiki/Visual_Basic_project_file",
	ext            : [".mak"],
	forbidExtMatch : true,
	magic          : ["Visual Basic project"]
};

exports.steps = [() => ({program : "strings"})];
