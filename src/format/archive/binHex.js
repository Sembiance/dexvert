"use strict";
const XU = require("@sembiance/xu"),
	C = require("../../C.js");

exports.meta =
{
	name      : "BinHex",
	website   : "http://fileformats.archiveteam.org/wiki/BinHex",
	ext       : [".hqx", ".hcx", ".hex"],
	magic     : C.TEXT_MAGIC,
	weakMagic : true
};

exports.converterPriority = ["unar", "deark"];
