"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Micrografx Draw/Designer",
	website        : "http://fileformats.archiveteam.org/wiki/Micrografx_Draw",
	ext            : [".drw", ".drt", ".ds4", ".dsf"],
	forbidExtMatch : true,
	magic          : ["Micrografx Designer Drawing"]
};

exports.converterPriority = ["scribus"];
