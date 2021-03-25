"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Funpaint",
	website : "http://fileformats.archiveteam.org/wiki/Funpaint",
	ext     : [".fp2", ".fun"],
	magic   : ["Funpaint 2 bitmap"]
};

exports.converterPriorty = ["recoil2png", "view64"];
