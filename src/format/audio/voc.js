"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Creative Voice",
	website : "http://fileformats.archiveteam.org/wiki/Creative_Voice_File",
	ext     : [".voc"],
	magic   : ["Creative Voice audio", "Creative Labs voice data"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.steps = [() => ({program : "sox"})];
