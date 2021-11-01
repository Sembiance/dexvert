/*
import {Format} from "../../Format.js";

export class ans extends Format
{
	name = "ANSI Art File";
	website = "http://fileformats.archiveteam.org/wiki/ANSI_Art";
	ext = [".ans",".drk",".ice",".ansi"];
	weakExt = [".drk",".ice"];
	forbidExtMatch = true;
	mimeType = "text/x-ansi";
	magic = ["ANSI escape sequence text","ISO-8859 text, with escape sequences","ASCII text","ISO-8859 text","UTF-8 Unicode text","Non-ISO extended-ASCII text","ReStructuredText file","International EBCDIC text","UTF-8 Unicode text","Printable ASCII","Unicode text, UTF-8 text","Algol 68 source, ISO-8859 text",{}];
	weakMagic = ["ASCII text","ISO-8859 text","UTF-8 Unicode text","Non-ISO extended-ASCII text","ReStructuredText file","International EBCDIC text","UTF-8 Unicode text","Printable ASCII","Unicode text, UTF-8 text","Algol 68 source, ISO-8859 text",{}];
	unsafe = true;
	converters = [{"program":"ansilove","flags":{"ansiloveType":"ans"}},"deark",{"program":"ffmpeg","flags":{"ffmpegFormat":"tty","ffmpegCodec":"ansi","ffmpegExt":".gif"}}]

inputMeta = undefined;
}
*/
/*
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

*/
