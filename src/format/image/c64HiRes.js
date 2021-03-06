"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name       : "C64 Hires-Bitmap",
	website    : "http://fileformats.archiveteam.org/wiki/Hires-Bitmap",
	ext        : [".hbm", ".hir", ".hpi", ".gih", ".fgs"],
	magic      : ["C64 Hires bitmap", "Koala Paint"], // Some .gif files start with koala paint magic, despite it not being that
	weakMagic  : true,
	trustMagic : true, // Koala Paint is normally untrustworthy, but we trust it here
	fileSize   : 8002
};

exports.converterPriorty = ["recoil2png", "view64"];
