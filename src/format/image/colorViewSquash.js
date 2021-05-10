"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "ColorViewSquash",
	website  : "http://fileformats.archiveteam.org/wiki/ColorViewSquash",
	ext      : [".rgb"],
	magic    : ["ColorViewSquash bitmap"]
};

exports.converterPriorty = ["recoil2png"];
