"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Funpaint",
	website        : "http://fileformats.archiveteam.org/wiki/Funpaint",
	ext            : [".fp2", ".fun"],
	forbidExtMatch : true,
	magic          : ["Funpaint 2 bitmap"]
};

exports.converterPriority = ["recoil2png", "view64"];
