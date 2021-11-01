"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Musicline Module",
	website : "https://www.musicline.org/",
	ext     : [".ml"],
	magic   : ["Musicline module"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = [{program : "uade123", flags : {uadeType : "MusiclineEditor"}}];
