"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name       : "Hi-Pic Creator",
	website    : "http://fileformats.archiveteam.org/wiki/Hi-Pic_Creator",
	ext        : [".hpc"],
	magic      : ["Koala Paint"], // Shares the same magic
	weakMagic  : true,
	trustMagic : true, // Koala Paint is normally untrustworthy, but we trust it here
	fileSize   : 9003
};

exports.converterPriority = ["recoil2png"];
