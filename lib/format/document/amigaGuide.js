"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Amigaguide Document",
	website  : "http://fileformats.archiveteam.org/wiki/AmigaGuide",
	ext      : [".guide"],
	magic    : ["Amigaguide hypertext document", "AmigaGuide file"]
};

exports.steps = [() => ({program : "grotag"})];
