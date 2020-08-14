"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name      : "P4I",
	website   : "http://fileformats.archiveteam.org/wiki/P4I",
	ext       : [".p4i"],
	magic     : ["Picasso 64 Image", "Saracen Paint Image", "Koala Paint (C64) bitmap"],
	weakMagic : true
};

exports.converterPriorty = ["recoil2png"];
