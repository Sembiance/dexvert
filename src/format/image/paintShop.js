"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "PaintShop",
	website : "http://fileformats.archiveteam.org/wiki/PaintShop",
	ext     : [".da4", ".psc"],
	magic   : ["PaintShop plus Compressed bitmap"]
};

exports.converterPriority = ["recoil2png"];
