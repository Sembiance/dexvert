"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Funny Paint",
	website        : "http://fileformats.archiveteam.org/wiki/Funny_Paint",
	ext            : [".fun"],
	forbidExtMatch : true,
	magic          : ["Funny Paint"]
};

exports.converterPriority = ["recoil2png"];
