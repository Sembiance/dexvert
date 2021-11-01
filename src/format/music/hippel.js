"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Hippel Module",
	website : "http://fileformats.archiveteam.org/wiki/Hippel",
	ext     : [".hip", ".hp", ".hip7", ".hipc", ".soc", ".sog"],
	magic   : ["Hippel module", "Hippel 7V module", "Hippel COmpressed SOng module", "Hippel-COSO Module sound file"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["uade123", {program : "uade123", flags : {uadeType : "JochenHippel_UADE"}}];
