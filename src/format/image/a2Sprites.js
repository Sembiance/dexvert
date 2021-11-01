"use strict";
const XU = require("@sembiance/xu"),
	C = require("../../C.js");

exports.meta =
{
	name          : "Apple II Sprites",
	ext           : [".spr"],
	magic         : C.TEXT_MAGIC,
	weakMagic     : true,
	untrustworthy : true
};

exports.converterPriority = ["recoil2png"];
