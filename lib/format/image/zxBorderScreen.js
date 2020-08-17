"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "ZX Spectrum Border Screen",
	website  : "http://fileformats.archiveteam.org/wiki/Border_Screen",
	ext      : [".bmc4", ".bsc"],
	filesize : [11136, 11904]
};

exports.converterPriorty = ["recoil2png"];
