"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name      : "GRASP Animation Archive",
	website   : "http://fileformats.archiveteam.org/wiki/GRASP_GL",
	ext       : [".gl"],
	magic     : ["GRASP animation"],
	weakMagic : true,
	notes     : "Several GL files don't play correctly with GRASP4 (PENCIL.GL, ROCKET.GL, SCISSORS.GL, KITE.GL, ACORN.GL, UMBRELLA.GL, v7vga.gl, l&hardy.gl, ICE.GL, COUNT.GL, LEAF.GL), likely need a later version."
};

exports.converterPriority = ["grasp4"];
