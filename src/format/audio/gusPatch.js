"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Gravis Ultrasound Patch",
	website        : "http://fileformats.archiveteam.org/wiki/Gravis_Ultrasound_patch",
	ext            : [".pat"],
	forbidExtMatch : true,
	magic          : ["GUS patch", "Gravis UltraSound GF1 patch"]
};

exports.converterPriority = ["awaveStudio"];
