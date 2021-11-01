"use strict";
const XU = require("@sembiance/xu"),
	C = require("../../C.js");

exports.meta =
{
	name           : "ANSI Art File",
	website        : "http://fileformats.archiveteam.org/wiki/ANSI_Art",
	ext            : [".ans", ".drk", ".ice", ".ansi"],
	weakExt        : [".drk", ".ice"],	// .ANS was widely accepted as ANSI, but .drk and .ice less so
	forbidExtMatch : true,
	mimeType       : "text/x-ansi",
	magic          : ["ANSI escape sequence text", "ISO-8859 text, with escape sequences", ...C.TEXT_MAGIC, /^data$/],
	weakMagic      : [...C.TEXT_MAGIC, /^data$/],
	unsafe         : true
};

exports.converterPriority = [{program : "ansilove", flags : {ansiloveType : "ans"}}, "deark", {program : "ffmpeg", flags : {ffmpegFormat : "tty", ffmpegCodec : "ansi", ffmpegExt : ".gif"}}];

exports.inputMeta = (state, p, cb) => p.family.ansiArtInputMeta(state, p, cb);
