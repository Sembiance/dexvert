"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "ANSI Art File",
	website        : "http://fileformats.archiveteam.org/wiki/ANSI_Art",
	ext            : [".ans", ".drk", ".ice"],
	forbidExtMatch : true,
	mimeType       : "text/x-ansi",
	magic          : ["ANSI escape sequence text"],
	unsafe         : true
};

exports.converterPriorty = [{program : "ansilove", flags : {ansiloveType : "ans"}}, "deark"];

exports.inputMeta = (state, p, cb) => p.family.ansiArtInputMeta(state, p, cb);
