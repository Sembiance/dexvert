"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Slight Atari Player",
	website : "http://fileformats.archiveteam.org/wiki/Slight_Atari_Player",
	ext     : [".sap"],
	magic   : ["Atari 8-bit SAP audio file", "Slight Atari Player music format "]
};

exports.converterPriorty = ["asapconv", "zxtune123"];
