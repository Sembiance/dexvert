"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "SoundFont 2.0",
	website     : "http://fileformats.archiveteam.org/wiki/SoundFont_2.0",
	ext         : [".sf2"],
	magic       : ["RIFF (little-endian) data SoundFont/Bank", "Standard SoundFont"],
	unsupported : true
};
