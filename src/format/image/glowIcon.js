"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Glow Icon",
	website : "http://fileformats.archiveteam.org/wiki/GlowIcons",
	ext     : [".info"],
	magic   : ["Amiga GlowIcon"]
};

exports.converterPriority = ["deark"];
