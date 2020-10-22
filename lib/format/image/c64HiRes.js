"use strict";
const XU = require("@sembiance/xu");
exports.meta =
{
	name       : "C64 Hires-Bitmap",
	website    : "http://fileformats.archiveteam.org/wiki/Hires-Bitmap",
	ext        : [".hbm", ".hir", ".hpi", ".gih", ".fgs"],
	magic      : ["C64 Hires bitmap"],
	weakMagic  : true,
	trustMagic : true,	// Magic is normally untrustworthy, but trust it in this case
	fileSize   : 8002
};

exports.converterPriorty = ["recoil2png"];
