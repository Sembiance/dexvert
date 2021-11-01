"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "MacBinary",
	website        : "http://fileformats.archiveteam.org/wiki/MacBinary",
	magic          : ["MacBinary 2", "MacBinary II"],
	ext            : [".bin"],
	forbidExtMatch : true,
	fallback       : true
};

exports.converterPriority = ["deark"];
