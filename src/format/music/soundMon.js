"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Brian Postma SoundMon module",
	website : "http://fileformats.archiveteam.org/wiki/Brian_Postma_SoundMon_v2.x_%26_v3.x_module",
	ext     : [".bp", ".bp3"],
	magic   : [/^BP SoundMon [123] module$/],
	notes   : "Not all files convert properly, such as CYBERSONG and SANXION"
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = [{program : "uade123", flags : {uadeType : "SoundMon2.0"}}, {program : "uade123", flags : {uadeType : "SoundMon2.2"}}];
