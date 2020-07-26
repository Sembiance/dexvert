"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "TheDraw File",
	website     : "http://fileformats.archiveteam.org/wiki/TheDraw_Save_File",
	ext         : [".td"],
	magic       : ["TheDraw design"],
	unsupported : true,
	notes       : XU.trim`
		ANSI Art drawing program for DOS. I couldn't come up with any converter programs for it nor could I locate a file format doc.
		I did locate MysticDraw for windows, which is supposed to be the successor, but I didn't try it and don't know if it can load TheDraw files and if it can, don't know if it can save em`
};
