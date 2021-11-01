"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "PC Screen Font",
	website : "http://fileformats.archiveteam.org/wiki/PC_Screen_Font",
	ext     : [".psf", ".psfu"],
	magic   : [/PC Screen Font/]
};

exports.steps = [() => ({program : "deark"})];
