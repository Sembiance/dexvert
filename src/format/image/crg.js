"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Calamus Raster Graphic",
	website : "http://fileformats.archiveteam.org/wiki/Calamus_Raster_Graphic",
	ext     : [".crg"],
	magic   : ["Calamus Raster Graphic bitmap"]
};

exports.converterPriorty = ["recoil2png", "deark", "nconvert"];
