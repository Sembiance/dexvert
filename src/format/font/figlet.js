"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "FIGlet Font",
	website : "http://fileformats.archiveteam.org/wiki/FIGlet_font",
	ext     : [".flf"],
	magic   : ["FIGfont", "FIGlet font"]
};

exports.steps = [() => ({program : "figlet"})];
