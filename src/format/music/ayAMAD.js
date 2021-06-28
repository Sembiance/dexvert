"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "AY Amadeus Chiptune",
	magic       : ["AY Amadeus chiptune"],
	ext         : [".amad"],
	unsupported : true,
	notes       : XU.trim`
		This program can play the files, even under linux, but couldn't figure out how to convert to WAV: https://bulba.untergrund.net/emulator_e.htm
		I tried several other programs like the AY To WAV converter here without luck: https://bulba.untergrund.net/progr_e.htm`
};
