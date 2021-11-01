"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "EZ-Art Professional",
	website : "http://fileformats.archiveteam.org/wiki/EZ-Art_Professional",
	ext     : [".eza"],
	magic   : ["EZ-Art Professional bitmap"]
};

exports.converterPriority = ["recoil2png"];
