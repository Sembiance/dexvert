"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Interpaint",
	website        : "http://fileformats.archiveteam.org/wiki/Interpaint",
	ext            : [".iph", ".ipt", ".lre", ".hre"],
	forbidExtMatch : true,
	magic          : ["Interpaint bitmap"],
	weakMagic      : true
};

exports.converterPriority = ["recoil2png", "nconvert", "view64"];
