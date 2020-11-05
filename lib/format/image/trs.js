"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "True Colour Sprites",
	website     : "http://fileformats.archiveteam.org/wiki/Spooky_Sprites",
	ext         : [".trs"],
	magic       : ["True Colour Sprites bitmap"],
	unsupported : true,
	notes       : XU.trim`
		There are a bunch of different versions of TRS files. Haven't found anything that can convert the sample files yet.
		This gets close, but crashes: https://github.com/ArguablyUseful/TRS_extraction
		This reports it can't handle the version of the sample files: https://github.com/dominions-tools/dominions-tools/blob/master/dump-trs-data`
};
