"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Hi-Pic Creator",
	website  : "http://fileformats.archiveteam.org/wiki/Hi-Pic_Creator",
	ext      : [".hpc"],
	magic    : ["Koala Paint"],	// Shares the same magic
	filesize : [9003]
};

exports.converterPriorty = ["recoil2png"];
