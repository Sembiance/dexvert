"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Wigmore Artist 64",
	website  : "http://fileformats.archiveteam.org/wiki/Wigmore_Artist_64",
	ext      : [".a64", ".wig"],
	mimeType : "image/x-artist-64"
};

exports.converterPriority = ["abydosconvert", "view64"];
