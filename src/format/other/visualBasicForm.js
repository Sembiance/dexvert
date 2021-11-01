"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Visual Basic Form",
	website        : "http://fileformats.archiveteam.org/wiki/VisualBasic_form",
	ext            : [".frm"],
	forbidExtMatch : true,
	magic          : ["Visual Basic Form"]
};

exports.steps = [() => ({program : "strings"})];
