"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name                : "ZX Spectrum Border Screen",
	website             : "http://fileformats.archiveteam.org/wiki/Border_Screen",
	ext                 : [".bmc4", ".bsc"],
	fileSize            : {".bsc" : 11136, ".bmc4" : 11904},
	forbidFileSizeMatch : true
};

exports.converterPriority = ["recoil2png"];
