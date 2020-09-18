"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "TUNDRA Text-Mode Graphic",
	website        : "http://fileformats.archiveteam.org/wiki/TUNDRA",
	ext            : [".tnd"],
	forbidExtMatch : true,
	mimeType       : "text/x-tundra",
	magic          : ["TUNDRA text-mode graphics"],
	bruteUnsafe    : true
};

exports.converterPriorty = [{program : "ansilove", stateFlags : {ansiloveType : "tnd"}}, "abydosconvert"];
