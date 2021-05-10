"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "FontForge File Format",
	website : "http://fileformats.archiveteam.org/wiki/Spline_Font_Database",
	ext     : [".sfd"],
	magic   : ["Spline Font Database"]
};

exports.steps = [() => ({program : "fontforge"})];
