"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "The Player Module",
	website : "http://fileformats.archiveteam.org/wiki/Amiga_Module",
	ext     : [".p61", ".p60", ".p50", ".p41", ".p40"],
	magic   : [/^The Player \d\.[01][ab] module$/]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.preSteps = [state => { state.uadeType = "PTK-Prowiz"; }];
exports.converterPriorty = ["xmp"];
exports.postSteps = [state => { delete state.uadeType; }];
