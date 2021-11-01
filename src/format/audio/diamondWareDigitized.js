"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "DiamondWare Digitized Audio",
	website        : "http://fileformats.archiveteam.org/wiki/DiamondWare_Digitized",
	ext            : [".dwd"],
	forbidExtMatch : true,
	magic          : ["DiamondWare Digitized audio"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["awaveStudio"];
