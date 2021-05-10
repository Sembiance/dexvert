"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "Slight Atari Player",
	website     : "http://fileformats.archiveteam.org/wiki/Slight_Atari_Player",
	ext         : [".sap"],
	unsupported : true,
	magic       : ["Atari 8-bit SAP audio file", "Slight Atari Player music format "],
	notes       : "A bit more modern of a format, haven't really looked into how best to support it yet."
};
