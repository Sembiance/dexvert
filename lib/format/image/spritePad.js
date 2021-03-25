"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "SpritePad",
	website : "http://www.subchristsoftware.com/spritepadfree/index.htm",
	ext     : [".spd"],
	magic   : ["Sprite Pad Data"]
};

exports.converterPriorty = ["recoil2png", "view64"];
