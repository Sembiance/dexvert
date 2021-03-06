"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "The Player Module",
	website : "http://fileformats.archiveteam.org/wiki/The_Player",
	ext     : [".p61", ".p61a", ".p60", ".p60a", ".p50", ".p50a", ".p41", ".p40", "p40a", ".p40b", ".p30", "p30a", ".p22", ".p22a"],
	magic   : [/^The Player \d\.[01][ab] module$/]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriorty = ["xmp", {program : "uade123", flags : {uadeType : "PTK-Prowiz"}}];
