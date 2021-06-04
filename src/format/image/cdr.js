"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "CorelDraw Document",
	website : "http://fileformats.archiveteam.org/wiki/CorelDRAW",
	ext     : [".cdr", ".cdt", ".cdx", ".cpx"],
	magic   : ["CorelDraw Document", "CorelDraw Drawing"],
	unsafe  : true
};

exports.converterPriorty = ["scribus", "deark", "nconvert"];
