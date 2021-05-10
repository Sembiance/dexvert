"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "PlayStation TIM",
	website : "http://fileformats.archiveteam.org/wiki/TIM_(PlayStation_graphics)",
	ext     : [".tim"],
	magic   : ["TIM image", "PSX TIM"]
};

exports.converterPriorty = ["convert", "recoil2png"];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
