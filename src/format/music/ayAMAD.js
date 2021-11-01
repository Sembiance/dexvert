"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "AY Amadeus Chiptune",
	magic       : ["AY Amadeus chiptune"],
	ext         : [".amad"],
	unsupported : true,
	notes       : XU.trim`
		Ay_Emul can play these under linux, but they don't offer a command line conversion option.
		zxtune123 doesn't seem to support them either.
		I tried several other programs like the AY To WAV converter here without luck: https://bulba.untergrund.net/progr_e.htm`
};
