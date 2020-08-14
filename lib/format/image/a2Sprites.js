"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	C = require(path.join(__dirname, "..", "..", "C.js"));

exports.meta =
{
	name      : "Apple II Sprites",
	ext       : [".spr"],
	magic     : C.TEXT_MAGIC,
	weakMagic : true
};

exports.converterPriorty = ["recoil2png"];
