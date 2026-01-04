import {Format} from "../../Format.js";

export class opus extends Format
{
	name         = "Opus Audio";
	website      = "http://fileformats.archiveteam.org/wiki/Opus";
	ext          = [".opus"];
	magic        = ["Ogg data, Opus audio", "Opus compressed audio", "audio/x-opus+ogg", "soxi: opus", /^fmt\/946( |$)/];
	metaProvider = ["soxi"];
	converters   = ["sox[type:opus]", "ffmpeg[outType:mp3]"];
}
