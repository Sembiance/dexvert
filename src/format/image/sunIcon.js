"use strict";
const XU = require("@sembiance/xu"),
	C = require("../../C.js");

exports.meta =
{
	name      : "Sun Icon",
	website   : "http://fileformats.archiveteam.org/wiki/Sun_icon",
	ext       : [".ico", ".icon"],
	magic     : C.TEXT_MAGIC,
	weakMagic : true,
	notes     : "Color currently isn't supported. Don't know of a converter that supports it due to palettes not being embedded within the file."
};

exports.converterPriority = ["nconvert"];
