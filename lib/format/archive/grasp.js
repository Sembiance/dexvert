"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name      : "GRASP Animation Archive",
	website   : "http://fileformats.archiveteam.org/wiki/GRASP_GL",
	ext       : [".gl"],
	magic     : ["GRASP animation"],
	weakMagic : true,
	notes     : XU.trim`
		This is an animation format, but the GRASPRT.EXE program won't play any of them and I can't find any modern players.
		However 'deark' will extract all the files, the artwork, code, etc. So for now I just treat this as an archive file.`
};

exports.steps = [() => ({program : "deark"})];
