"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name      : "Oric Font",
	ext       : [".chs"],
	magic     : ["Oric Tape image"],
	weakMagic : true
};

exports.steps = [() => ({program : "recoil2png"})];
