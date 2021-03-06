"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Multiple-image Network Graphics",
	website  : "http://fileformats.archiveteam.org/wiki/MNG",
	ext      : [".mng"],
	mimeType : "video/x-mng",
	magic    : ["Multiple-image Network Graphics bitmap", "MNG video data"]
};

exports.converterPriorty = [{program : "convert", flags : {convertExt : ".webp"}}];
exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
