"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Drazlace",
	website : "http://fileformats.archiveteam.org/wiki/Dir_Logo_Maker",
	ext     : [".drl", ".dlp"],
	magic   : ["Drazlace bitmap"]
};

exports.converterPriorty = ["recoil2png", "view64"];
