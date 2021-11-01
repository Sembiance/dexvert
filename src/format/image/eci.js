"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "ECI Graphic Editor",
	website  : "http://fileformats.archiveteam.org/wiki/ECI_Graphic_Editor",
	ext      : [".eci", ".ecp"]
};

exports.converterPriority = ["recoil2png", "view64"];
