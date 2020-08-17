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
	bruteUnsafe    : true
};

// Deark seems to handle .ans the best, ansilove fails on some images such as "WZ - Portrait Blonde.ans"
exports.converterPriorty = ["deark", "ansilove"];

exports.inputMeta = (state, p, cb) => p.family.ansiArtInputMeta(state, p, cb);
