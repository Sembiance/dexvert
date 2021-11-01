"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "WAD",
	website : "http://fileformats.archiveteam.org/wiki/Doom_WAD",
	ext     : [".wad"],
	magic   : ["id Software's DOOM Patch-WAD", "doom patch PWAD", "doom main IWAD", "id Software's DOOM Internal-WAD"]
};

exports.converterPriority = ["deark", "gameextractor"];
