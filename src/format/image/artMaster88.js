"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "ArtMaster88",
	website  : "http://fileformats.archiveteam.org/wiki/ArtMaster88",
	ext      : [".img"],
	magic    : ["ArtMaster88"],
	mimeType : "image/x-artmaster"
};

exports.converterPriorty = ["recoil2png", "abydosconvert"];
