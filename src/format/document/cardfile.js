"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Cardfile Document",
	website : "http://fileformats.archiveteam.org/wiki/Cardfile",
	ext     : [".crd"],
	magic   : ["Windows Cardfile database", "Cardfile"]
};

exports.steps =
[
	() => ({program : "deark"}),
	() => ({program : "cardfile"})
];
