"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "MoPaQ Archive",
	ext            : [".mpq"],
	magic          : ["MoPaQ (MPQ) archive", "MPQ Archive"],
	forbiddenMagic : ["StarCraft Map"],
	unsupported    : true,
	notes          : "Need some sample archives. Can use this to extract: https://github.com/Kanma/MPQExtractor or https://github.com/uakfdotb/umpqx"
};
