"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Amiga XPK Archive",
	website : "http://fileformats.archiveteam.org/wiki/XPK",
	ext     : [".xpk"],
	magic   : ["Amiga xpkf.library compressed data", "XPK compressed data"]
};

exports.converterPriority = ["amigadepacker", "ancient", "xfdDecrunch"];
