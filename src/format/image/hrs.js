"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name      : "Oric HRS",
	ext       : [".hrs", ".hir"],
	magic     : ["Oric Tape Image"],
	weakMagic : true
};

exports.converterPriority = ["recoil2png"];
