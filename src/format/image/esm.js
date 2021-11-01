"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Enhanced Simplex",
	website  : "http://fileformats.archiveteam.org/wiki/Enhanced_Simplex",
	ext      : [".esm"],
	magic    : ["Enhanced Simplex bitmap"]
};

exports.converterPriority = ["recoil2png", "nconvert"];
