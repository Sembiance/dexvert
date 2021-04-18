"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "AdLib Instrument Bank",
	website     : "http://fileformats.archiveteam.org/wiki/AdLib_instrument_bank",
	ext         : [".bnk"],
	magic       : ["Adlib instruments/sound bank"],
	weakMagic   : true,
	unsupported : true,
	notes       : XU.trim`
		These .bnk files include sounds/instruments used by adlib ROL/SNG/SX files to make music.
		Technically the sounds could be extracted, maybe with 'Bank Manager' for DOS, but meh.
		Awave Studio claims to support these, but under version 7 I couldn't get them to load.`
};
