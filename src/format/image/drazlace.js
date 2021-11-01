"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Drazlace",
	website        : "http://fileformats.archiveteam.org/wiki/Dir_Logo_Maker",
	ext            : [".drl", ".dlp"],
	forbidExtMatch : true,
	magic          : ["Drazlace bitmap"]
};

exports.converterPriority = ["recoil2png", "view64"];
