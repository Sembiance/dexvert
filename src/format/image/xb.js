"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Extended Binary",
	website        : "http://fileformats.archiveteam.org/wiki/XBIN",
	ext            : [".xb"],
	forbidExtMatch : true,
	mimeType       : "image/x-xbin",
	magic          : ["XBIN image"],
	unsafe    : true
};

exports.converterPriority = [{program : "ansilove", flags : {ansiloveType : "xb"}}, "deark", "abydosconvert"];

exports.inputMeta = (state, p, cb) => p.family.ansiArtInputMeta(state, p, cb);
