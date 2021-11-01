"use strict";
const XU = require("@sembiance/xu"),
	C = require("../../C.js");

exports.meta =
{
	name      : "ZXpaintyONE",
	website   : "https://web.archive.org/web/20160507112745/http://matt.west.co.tt/demoscene/zxpaintyone/",
	ext       : [".zp1"],
	magic     : C.TEXT_MAGIC,
	weakMagic : true
};

exports.converterPriority = ["recoil2png"];
