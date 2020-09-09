"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	C = require(path.join(__dirname, "..", "..", "C.js"));

exports.meta =
{
	name      : "Sixel",
	website   : "https://en.wikipedia.org/wiki/Sixel",
	ext       : [".six", ".sixel"],
	mimeType  : "image/x-sixel",
	magic     : C.TEXT_MAGIC,
	weakMagic : true
};

exports.converterPriorty = ["abydosconvert"];
