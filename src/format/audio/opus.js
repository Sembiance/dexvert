import {Format} from "../../Format.js";

export class opus extends Format
{
	name         = "Opus Audio";
	website      = "http://fileformats.archiveteam.org/wiki/Opus";
	ext          = [".opus"];
	magic        = ["Ogg data, Opus audio", "Opus compressed audio", "audio/x-opus+ogg", /^fmt\/946( |$)/];
	metaProvider = ["soxi"];
	converters   = ["sox", "ffmpeg[outType:mp3]"];
}
