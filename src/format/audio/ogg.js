"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Ogg Vorbis Audio",
	website : "http://fileformats.archiveteam.org/wiki/Ogg",
	ext     : [".ogg", ".oga"],
	magic   : ["OGG Vorbis audio", "Ogg data, Vorbis audio"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.steps = [() => ({program : "sox"})];
