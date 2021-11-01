"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "InShape 3D IIM",
	website : "http://fileformats.archiveteam.org/wiki/InShape_IIM",
	ext     : [".iim"],
	magic   : ["InShape IIM bitmap"]
};

exports.converterPriority = ["recoil2png"];
