"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name       : "P4I",
	website    : "http://fileformats.archiveteam.org/wiki/P4I",
	ext        : [".p4i"],
	magic      : ["Picasso 64 Image", "Saracen Paint Image", "Koala Paint"],
	weakMagic  : true,
	trustMagic : true // Koala Paint is normally untrustworthy, but we trust it here
};

exports.converterPriority = ["recoil2png"];
