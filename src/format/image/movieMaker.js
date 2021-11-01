"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Movie Maker",
	website  : "http://fileformats.archiveteam.org/wiki/Movie_Maker",
	ext      : [".bkg", ".shp"],
	fileSize : {".bkg" : 3856, ".shp" : [1024, 4384]}
};

exports.converterPriority = ["recoil2png"];
