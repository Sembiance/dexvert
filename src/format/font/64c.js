"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name      : "C64 8x8 Font",
	ext       : [".64c"],
	magic     : ["C64 8x8 font bitmap"],
	weakMagic : true
};

exports.steps = [() => ({program : "recoil2png"})];
