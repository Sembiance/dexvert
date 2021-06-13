"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Word Document",
	website        : "http://fileformats.archiveteam.org/wiki/DOC",
	ext            : [".doc"],
	forbidExtMatch : true,
	magic          : ["Microsoft Word document"],
	unsafe         : true
};

exports.steps = [() => ({program : "soffice"})];
