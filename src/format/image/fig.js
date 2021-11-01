"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "XFig",
	website : "http://fileformats.archiveteam.org/wiki/Fig",
	ext     : [".fig"],
	magic   : ["FIG image text", "FIG vector drawing"],
	notes   : "It's a vector format, but embedded bitmaps don't convert to SVG. So we convert to both SVG and PNG."
};

exports.steps = [
	() => ({program : "fig2dev", flags : {fig2devType : "png"}}),
	() => ({program : "fig2dev"})
];
