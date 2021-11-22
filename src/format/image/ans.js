/*
import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";

export class ans extends Format
{
	name           = "ANSI Art File";
	website        = "http://fileformats.archiveteam.org/wiki/ANSI_Art";
	ext            = [".ans", ".drk", ".ice", ".ansi"];
	weakExt        = [".drk", ".ice"];	// .ANS was widely accepted as ANSI, but .drk and .ice less so
	forbidExtMatch = true;
	mimeType       = "text/x-ansi";
	magic          = ["ANSI escape sequence text", "ISO-8859 text, with escape sequences", ...TEXT_MAGIC, /^data$/];
	weakMagic      = [...TEXT_MAGIC, /^data$/];
	metaProviders  = ["ansiArt"];
	converters     = ["ansilove[format:ans]", "deark", "ffmpeg[format:tty][codec:ansi][outType:gif]"];
	//converters     = [{program : "ansilove", flags : {ansiloveType : "ans"}}, "deark", {program : "ffmpeg", flags : {ffmpegFormat : "tty", ffmpegCodec : "ansi", ffmpegExt : ".gif"}}];
}
*/
